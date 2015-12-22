import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import datetime as dt
pd.set_option('max_columns', 50)
mpl.rcParams['lines.linewidth'] = 2


def cohort_analysis(raw_data):
    df = pd.read_csv(raw_data, usecols=['keen.timestamp', 'page.pk', 'user.pk'])
    df.rename(columns={'keen.timestamp': 'keen_timestamp',
                       'user.pk': 'user_pk',
                       'page.pk': 'page_pk'}, inplace=True)

    df['OrderPeriod'] = df.keen_timestamp.apply(lambda x: dt.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.%fZ').
                                                strftime('%Y-%m'))

    df.set_index('user_pk', inplace=True)
    df['CohortGroup'] = df.groupby(level=0)['keen_timestamp'].min().apply(lambda x:
                                                                          dt.datetime.strptime
                                                                          (x, '%Y-%m-%dT%H:%M:%S.%fZ').
                                                                          strftime('%Y-%m'))
    df.reset_index(inplace=True)
    grouped = df.groupby(['CohortGroup', 'OrderPeriod'])
    # count the unique users, orders, and total revenue per Group + Period
    cohorts = grouped.agg({'user_pk': pd.Series.nunique,
                           'page_pk': pd.Series.nunique})
    # make the column names more meaningful
    cohorts.rename(columns={'user_pk': 'TotalUsers',
                            'page_pk': 'TotalPages'}, inplace=True)
    # method to determine how each cohort as behaved in the months following their initial use
    cohorts = cohorts.groupby(level=0).apply(cohort_period)
    # reindex the DataFrame
    cohorts.reset_index(inplace=True)
    cohorts.set_index(['CohortGroup', 'CohortPeriod'], inplace=True)
    # create a Series holding the total size of each CohortGroup
    cohort_group_size = cohorts['TotalUsers'].groupby(level=0).first()
    user_retention = cohorts['TotalUsers'].unstack(0).divide(cohort_group_size, axis=1)
    user_retention.to_pickle('user_retention.pickle')

    user_retention[['2015-06', '2015-07', '2015-08']].plot(figsize=(10, 5))
    plt.title('Cohorts: User Retention')
    plt.xticks(np.arange(1, 12.1, 1))
    plt.xlim(1, 12)
    plt.ylabel('% of Cohort Purchasing')

    plt.figure(figsize=(12, 8))
    plt.title('Cohorts: User Retention')
    sns.heatmap(user_retention.T, mask=user_retention.T.isnull(), annot=True, fmt='.0%', cmap="Greens")
    plt.show()


def cohort_period(df):
        """
        Creates a `CohortPeriod` column, which is the Nth period based on the user's first purchase.
        Example
        -------
        Say you want to get the 3rd month for every user:
            df.sort(['UserId', 'OrderTime', inplace=True)
            df = df.groupby('UserId').apply(cohort_period)
            df[df.CohortPeriod == 3]
        """
        df['CohortPeriod'] = np.arange(len(df)) + 1
        return df
