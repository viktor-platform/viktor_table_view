"""This module provides the TableView and TableResult, to be used in VIKTOR applications as view wrapper and return
respectively
"""
from pathlib import Path
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union

import pandas as pd
from pandas.io.formats.style import Styler
from viktor import File
from viktor.utils import render_jinja_template
from viktor.views import WebResult
from viktor.views import WebView

TableView = WebView


class TableResult(WebResult):
    """Class to generate a table result in a VIKTOR web application.

    dataframe: The dataframe to be displayed
    dataframe_colours: The same format as the inputted dataframe, yet with all values replaced by one of the following:
        - "success"
        - "error"
        - "info"
        - "warning"
        - pd.NA (these will be replaced by "info")
        All these will be transformed to a color upon rendering
    n_decimals: number of decimals that all floats should be rounded to. Can also be given as a dictionary:
        {"column_name_A": 2, "column_name_B": 4}
    style: Custom styles can be defined beforehand. Apply the styles on the Styler object and pass to this class
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        n_decimals: Optional[Union[int, Dict[Union[str, Tuple[str, ...]], int]]] = None,
        dataframe_colours: Optional[pd.DataFrame] = None,
        style: Optional[Styler] = None,
    ):
        self.dataframe = dataframe.copy(deep=True)
        self.style = style or self.dataframe.style
        self.update_header_style()
        self.dataframe_colours = dataframe_colours
        self.n_decimals = n_decimals
        super().__init__(html=self.get_html())

    @property
    def float_columns(self) -> Union[pd.Index, pd.MultiIndex]:
        """Returns the column indices that are floats"""
        return self.dataframe.select_dtypes(include=[float]).columns

    def format_dataframe(self):
        """Formats the dataframe to prepare it for showing in a WebResult"""
        # Round the float values to their respective numbers
        if isinstance(self.n_decimals, int):
            self.style.format(precision=self.n_decimals)
        elif isinstance(self.n_decimals, dict):
            for column_key, n_decimals in self.n_decimals.items():
                self.dataframe[column_key] = self.dataframe[column_key].round(n_decimals).astype(str)
        # Colourize the values using some formatter function
        if isinstance(self.dataframe_colours, pd.DataFrame):
            self.dataframe_colours.fillna("info")
            self.style.set_td_classes(self.dataframe_colours)

    def get_html(self) -> File:
        """Get the html to be displayed"""
        self.format_dataframe()
        header_style = {
            "selector": "th",
            "props": [("text-align", "center"), ("background-color", "rgba(245, 245, 252)")],
        }
        self.style.set_table_styles([header_style])
        with open(Path(__file__).parent / "table.html.jinja", "rb") as template:
            result = render_jinja_template(
                template, {"table_html": self.style.to_html(table_attributes='class="table table-hover"')}
            )
        return result

    def update_header_style(self):
        """Updates header style if no header style is added to the styler"""
        has_header_style = False
        if self.style.table_styles:
            for table_style in self.style.table_styles:
                if "th" in table_style.values():
                    has_header_style = True
                    break
        if not has_header_style or self.style.table_styles is None:
            header_style = {
                "selector": "th",
                "props": [("text-align", "center"), ("background-color", "rgba(245, 245, 252)")],
            }
            self.style.set_table_styles([header_style])
