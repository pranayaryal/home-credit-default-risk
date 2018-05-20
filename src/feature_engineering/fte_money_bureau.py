# Copyright 2018 Mamy André-Ratsimbazafy. All rights reserved.

import pandas as pd

def fte_prev_credit_situation(train, test, y, db_conn, folds, cache_file):
  def _trans(df, table):
    query = f"""
    select
      IFNULL(count(b.SK_ID_CURR), 0) AS total_prev_applications,
      IFNULL(sum(case CREDIT_ACTIVE when 'Active' then 1 else 0 end), 0) AS current_active_applications,
      IFNULL(sum(AMT_CREDIT_SUM), 0) AS total_prev_credit,
      IFNULL(sum(case CREDIT_ACTIVE when 'Active' then AMT_CREDIT_SUM else 0 end), 0) AS active_credit_amount,
      IFNULL(sum(AMT_CREDIT_SUM_DEBT), 0) AS current_debt,
      IFNULL(sum(AMT_CREDIT_MAX_OVERDUE), 0) AS current_overdue,
      IFNULL(max(-DAYS_CREDIT / 365.25), 99) AS first_credit_years_ago,
      IFNULL(min(-DAYS_CREDIT / 365.25), 99) AS last_credit_years_ago
    from
      {table} app
    left join
      bureau b on app.SK_ID_CURR = b.SK_ID_CURR
    GROUP BY
      app.SK_ID_CURR
    ORDER BY
      app.SK_ID_CURR ASC;
    """

    df[['total_prev_applications',
        'current_active_applications',
        'total_prev_credit',
        'active_credit_amount',
        'current_debt',
        'current_overdue',
        'first_credit_years_ago',
        'last_credit_years_ago']] = pd.read_sql_query(query, db_conn)

    # TODO add currency, otherwise credit is not comparable

  _trans(train, "application_train")
  _trans(test, "application_test")

  return train, test, y, db_conn, folds, cache_file
