import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

pd.set_option('max_columns', 50)
mpl.rcParams['lines.linewidth'] = 2


def cohort_stuff():
    df = pd.read_excel('chapter-12-relay-foods.xlsx')

    df['OrderPeriod'] = df.OrderDate.apply(lambda x: x.strftime('%Y-%m'))

    df.set_index('UserId', inplace=True)

    df['CohortGroup'] = df.groupby(level=0)['OrderDate'].min().apply(lambda x: x.strftime('%Y-%m'))

    df.reset_index(inplace=True)

    grouped = df.groupby(['CohortGroup', 'OrderPeriod'])

    # count the unique users, orders, and total revenue per Group + Period
    cohorts = grouped.agg({'UserId': pd.Series.nunique,
                           'OrderId': pd.Series.nunique,
                           'TotalCharges': np.sum})

    # make the column names more meaningful
    cohorts.rename(columns={'UserId': 'TotalUsers',
                            'OrderId': 'TotalOrders'}, inplace=True)

    # method to determine how each cohort as behaved in the months following their initial use
    cohorts = cohorts.groupby(level=0).apply(cohort_period)

    # reindex the DataFrame
    cohorts.reset_index(inplace=True)
    cohorts.set_index(['CohortGroup', 'CohortPeriod'], inplace=True)

    # create a Series holding the total size of each CohortGroup
    cohort_group_size = cohorts['TotalUsers'].groupby(level=0).first()

    user_retention = cohorts['TotalUsers'].unstack(0).divide(cohort_group_size, axis=1)
    print(user_retention.head())

    user_retention[['2009-06', '2009-07', '2009-08']].plot(figsize=(10, 5))
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

cohort_stuff()