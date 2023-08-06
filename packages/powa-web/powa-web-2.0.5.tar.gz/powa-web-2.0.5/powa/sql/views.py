from sqlalchemy.sql import (select, cast, func, column, text, extract, case,
                            bindparam, literal_column, ColumnCollection)
from sqlalchemy.types import Numeric
from sqlalchemy.sql.functions import max, min, sum
from powa.sql.utils import *
from powa.sql import resolve_quals
from collections import defaultdict


class Biggest(object):

    def __init__(self, base_columns, order_by):
        self.base_columns = base_columns
        self.order_by = order_by

    def __call__(self, var, minval=0, label=None):
        label = label or var
        return func.greatest(
            func.lead(column(var))
            .over(order_by=self.order_by,
                  partition_by=self.base_columns)
                - column(var),
            minval).label(label)


def powa_base_statdata_detailed_db():
    base_query = text("""
    pg_database,
    LATERAL
    (
        SELECT unnested.dbid, unnested.queryid,(unnested.records).*
        FROM (
            SELECT psh.dbid, psh.queryid, psh.coalesce_range, unnest(records) AS records
            FROM powa_statements_history psh
            WHERE coalesce_range && tstzrange(:from, :to, '[]')
            AND psh.dbid = pg_database.oid
            AND psh.queryid IN ( SELECT powa_statements.queryid FROM powa_statements WHERE powa_statements.dbid = pg_database.oid )
        ) AS unnested
        WHERE tstzrange(:from, :to, '[]') @> (records).ts
        UNION ALL
        SELECT psc.dbid, psc.queryid,(psc.record).*
        FROM powa_statements_history_current psc
        WHERE tstzrange(:from,:to,'[]') @> (record).ts
        AND psc.dbid = pg_database.oid
        AND psc.queryid IN ( SELECT powa_statements.queryid FROM powa_statements WHERE powa_statements.dbid = pg_database.oid )
    ) h
    """)
    return base_query

def powa_base_statdata_db():
    base_query = text("""
    (
    SELECT pg_database.oid as dbid, h.*
    FROM
    pg_database LEFT JOIN
    (
          SELECT dbid, min(lower(coalesce_range)) AS min_ts, max(upper(coalesce_range)) AS max_ts
          FROM powa_statements_history_db dbh
          WHERE coalesce_range && tstzrange(:from, :to, '[]')
          GROUP BY dbid
    ) ranges ON pg_database.oid = ranges.dbid,
    LATERAL (
        SELECT (unnested1.records).*
        FROM (
            SELECT dbh.coalesce_range, unnest(records) AS records
            FROM powa_statements_history_db dbh
            WHERE coalesce_range @> min_ts
            AND dbh.dbid = ranges.dbid
        ) AS unnested1
        WHERE tstzrange(:from, :to, '[]') @> (unnested1.records).ts
        UNION ALL
        SELECT (unnested2.records).*
        FROM (
            SELECT dbh.coalesce_range, unnest(records) AS records
            FROM powa_statements_history_db dbh
            WHERE coalesce_range @> max_ts
            AND dbh.dbid = ranges.dbid
        ) AS unnested2
        WHERE tstzrange(:from, :to, '[]') @> (unnested2.records).ts
        UNION ALL
        SELECT (dbc.record).*
        FROM powa_statements_history_current_db dbc
        WHERE tstzrange(:from, :to, '[]') @> (dbc.record).ts
        AND dbc.dbid = pg_database.oid
    ) AS h) AS db_history
    """)
    return base_query

def get_diffs_forstatdata():
    return [
        diff("calls"),
        diff("total_time").label("runtime"),
        diff("shared_blks_read"),
        diff("shared_blks_hit"),
        diff("shared_blks_dirtied"),
        diff("shared_blks_written"),
        diff("temp_blks_read"),
        diff("temp_blks_written"),
        diff("blk_read_time"),
        diff("blk_write_time")
    ]

def powa_getstatdata_detailed_db():
    base_query = powa_base_statdata_detailed_db()
    diffs = get_diffs_forstatdata()
    return (select([
        column("queryid"),
        column("dbid"),
        column("datname"),
] + diffs)
        .select_from(base_query)
        .group_by(column("queryid"), column("dbid"), column("datname"))
        .having(max(column("calls")) - min(column("calls")) > 0))

def powa_getstatdata_db():
    base_query = powa_base_statdata_db()
    diffs = get_diffs_forstatdata()
    return (select([column("dbid")] + diffs)
            .select_from(base_query)
            .group_by(column("dbid"))
            .having(max(column("calls")) - min(column("calls")) > 0))


BASE_QUERY_SAMPLE_DB = text("""(
    SELECT datname, base.* FROM pg_database,
    LATERAL (
        SELECT *
        FROM (
            SELECT
            row_number() OVER (PARTITION BY dbid ORDER BY statements_history.ts) AS number,
            count(*) OVER (PARTITION BY dbid) AS total,
            *
            FROM (
                SELECT dbid, (unnested.records).*
                FROM (
                    SELECT psh.dbid, psh.coalesce_range, unnest(records) AS records
                    FROM powa_statements_history_db psh
                    WHERE coalesce_range && tstzrange(:from, :to,'[]')
                    AND psh.dbid = pg_database.oid
                ) AS unnested
                WHERE tstzrange(:from, :to, '[]') @> (records).ts
                UNION ALL
                SELECT dbid, (record).*
                FROM powa_statements_history_current_db
                WHERE tstzrange(:from, :to, '[]') @> (record).ts
                AND dbid = pg_database.oid
            ) AS statements_history
        ) AS sh
        WHERE number % ( int8larger((total)/(:samples+1),1) ) = 0
    ) AS base
) AS by_db
""")

BASE_QUERY_SAMPLE = text("""(
    SELECT datname, dbid, queryid, base.*
    FROM powa_statements JOIN pg_database ON pg_database.oid = powa_statements.dbid,
    LATERAL (
        SELECT *
        FROM (SELECT
            row_number() OVER (PARTITION BY queryid ORDER BY statements_history.ts) AS number,
            count(*) OVER (PARTITION BY queryid) AS total,
            *
            FROM (
                SELECT (unnested.records).*
                FROM (
                    SELECT psh.queryid, psh.coalesce_range, unnest(records) AS records
                    FROM powa_statements_history psh
                    WHERE coalesce_range && tstzrange(:from, :to, '[]')
                    AND psh.queryid = powa_statements.queryid
                ) AS unnested
                WHERE tstzrange(:from, :to, '[]') @> (records).ts
                UNION ALL
                SELECT (record).*
                FROM powa_statements_history_current phc
                WHERE tstzrange(:from, :to, '[]') @> (record).ts
                AND phc.queryid = powa_statements.queryid
            ) AS statements_history
        ) AS sh
        WHERE number % ( int8larger((total)/(:samples+1),1) ) = 0
    ) AS base
) AS by_query
""")


def powa_getstatdata_sample(mode):
    if mode == "db":
        base_query = BASE_QUERY_SAMPLE_DB
        base_columns = ["dbid"]

    elif mode == "query":
        base_query = BASE_QUERY_SAMPLE
        base_columns = ["dbid", "queryid"]

    ts = column('ts')
    biggest = Biggest(base_columns, ts)


    return select(base_columns + [
        ts,
        biggest("ts", '0 s', "mesure_interval"),
        biggest("calls"),
        biggest("total_time", label="runtime"),
        biggest("rows"),
        biggest("shared_blks_read"),
        biggest("shared_blks_hit"),
        biggest("shared_blks_dirtied"),
        biggest("shared_blks_written"),
        biggest("local_blks_read"),
        biggest("local_blks_hit"),
        biggest("local_blks_dirtied"),
        biggest("local_blks_written"),
        biggest("temp_blks_read"),
        biggest("temp_blks_written"),
        biggest("blk_read_time"),
        biggest("blk_write_time")]).select_from(base_query).apply_labels()


def qualstat_base_statdata():
    base_query = text("""
    (
    SELECT queryid, qualid, (unnested.records).*
    FROM (
        SELECT pqnh.qualid, pqnh.queryid, pqnh.dbid, pqnh.userid, pqnh.coalesce_range, unnest(records) as records
        FROM powa_qualstats_quals_history pqnh
        WHERE coalesce_range  && tstzrange(:from, :to, '[]') AND pqnh.queryid = :query
    ) AS unnested
    WHERE tstzrange(:from, :to, '[]') @> (records).ts
    UNION ALL
    SELECT queryid, qualid, pqnc.ts, pqnc.count, pqnc.nbfiltered
    FROM powa_qualstats_quals_history_current pqnc
    WHERE tstzrange(:from, :to, '[]') @> pqnc.ts AND pqnc.queryid = :query
    ) h
    JOIN powa_qualstats_quals pqnh USING (queryid, qualid)
    """)
    return base_query


def qualstat_getstatdata():
    base_query = qualstat_base_statdata()
    return (select([
        column("qualid"),
        column("queryid").label("queryid"),
        func.to_json(column("quals")).label("quals"),
        sum(column("count")).label("count"),
        sum(column("nbfiltered")).label("nbfiltered"),
        case(
            [(sum(column("count")) == 0, 0)],
            else_=sum(column("nbfiltered")) /
                cast(sum(column("count")), Numeric)
        ).label("filter_ratio")])
        .select_from(base_query)
        .group_by(column("qualid"), literal_column("queryid"), column("quals")))

def possible_indexes(resolved_qual_list):
    by_am = defaultdict(list)
    for qual in resolved_qual_list:
        for am in qual['indexam_names']:
            by_am[am].append(qual)
    return by_am


BASE_QUERY_KCACHE_SAMPLE = text("""
        powa_statements s JOIN pg_database ON pg_database.oid = s.dbid,
        LATERAL (
            SELECT *
            FROM (
                SELECT row_number() OVER (ORDER BY kmbq.ts) AS number,
                    count(*) OVER () as total,
                        *
                FROM (
                    SELECT km.ts,
                    sum(km.reads) AS reads, sum(km.writes) AS writes,
                    sum(km.user_time) AS user_time, sum(km.system_time) AS system_time
                    FROM (
                        SELECT * FROM (
                            SELECT (unnest(metrics)).*
                            FROM powa_kcache_metrics km
                            WHERE km.queryid = s.queryid
                            AND km.coalesce_range && tstzrange(:from, :to, '[]')
                        ) his
                        WHERE tstzrange(:from, :to, '[]') @> his.ts
                        UNION ALL
                        SELECT (metrics).*
                        FROM powa_kcache_metrics_current kmc
                        WHERE tstzrange(:from, :to, '[]') @> (metrics).ts
                        AND kmc.queryid = s.queryid
                    ) km
                    GROUP BY km.ts
                ) kmbq
            ) kmn
        WHERE kmn.number % (int8larger(total/(:samples+1),1) ) = 0
        ) kcache
""")

def kcache_getstatdata_sample():
    base_query = BASE_QUERY_KCACHE_SAMPLE
    base_columns = ["queryid", "datname"]
    ts = column('ts')
    biggest = Biggest(base_columns, ts)

    return (select(base_columns + [
        ts,
        biggest("reads"),
        biggest("writes"),
        biggest("user_time"),
        biggest("system_time")])
        .select_from(base_query)
        .apply_labels())
