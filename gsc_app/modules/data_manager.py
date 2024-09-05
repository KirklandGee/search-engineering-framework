import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class DataManager:
    def __init__(self, df):
        self.df = df

    def clean_data(self):
        """
        Clean the dataframe by removing duplicates and handling missing values.
        """
        self.df = self.df.drop_duplicates()
        self.df = self.df.fillna(0)  # Replace NaN with 0, adjust as needed
        return self

    def calculate_metrics(self):
        """
        Calculate additional metrics based on existing data.
        """
        if 'clicks' in self.df.columns and 'impressions' in self.df.columns:
            self.df['ctr'] = self.df['clicks'] / self.df['impressions']
        return self

    def sort_data(self, column, ascending=False):
        """
        Sort the dataframe by a specified column.
        """
        self.df = self.df.sort_values(by=column, ascending=ascending)
        return self

    def filter_data(self, column, condition):
        """
        Filter the dataframe based on a condition.
        """
        self.df = self.df[self.df[column].apply(condition)]
        return self

    def generate_summary(self):
        """
        Generate a summary of the dataframe.
        """
        summary = self.df.describe()
        return summary


    def plot_data(self, x_column, y_column, plot_type='scatter'):
        """
        Create a plot based on specified columns and plot type.
        """
        plt.figure(figsize=(10, 6))
        if plot_type == 'scatter':
            sns.scatterplot(data=self.df, x=x_column, y=y_column)
        elif plot_type == 'line':
            sns.lineplot(data=self.df, x=x_column, y=y_column)
        elif plot_type == 'bar':
            sns.barplot(data=self.df, x=x_column, y=y_column)
        plt.title(f'{y_column} vs {x_column}')
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        return plt

    def export_data(self, filename, file_format='csv'):
        """
        Export the dataframe to a file.
        """
        if file_format == 'csv':
            self.df.to_csv(filename, index=False)
        elif file_format == 'excel':
            self.df.to_excel(filename, index=False)
        elif file_format == 'json':
            self.df.to_json(filename, orient='records')
