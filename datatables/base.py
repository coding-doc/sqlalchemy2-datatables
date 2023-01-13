from typing import Any, Callable

from pydantic import BaseModel


class DTKey:
    ROW_ID: str = 'DT_RowId'
    ROW_CLASS: str = 'DT_RowClass'
    ROW_DATA: str = 'DT_RowData'
    ROW_ATTR: str = 'DT_RowAttr'


class DTDataCallbacks:
    get_row_id: Callable[[dict[str, Any]], str] | None = None
    get_row_class: Callable[[dict[str, Any]], str] | None = None
    get_row_data: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    get_row_attr: Callable[[dict[str, Any]], dict[str, Any]] | None = None

    def set_row_id_getter(self, getter: Callable[[dict[str, Any]], str]) -> None:
        """
        Set the lamda that will return the id value of the <tr> node of the datatable row.
        The lambda result will be used to update the result row with DT_RowId key value pair. This will
        set the id attribute of the <tr> node.
        :param: Callable - the lambda that has access to the result row (dict key: column name, value: column value)
                to produce the id value to be added to the <tr> node of the datatable
        """
        self.get_row_id = getter

    def set_row_class_getter(self, getter: Callable[[dict[str, Any]], str]) -> None:
        """
        Set the lamda that will return the class name of the <tr> node of the datatable row.
        The lambda result will be used to update the result row with DT_RowClass key value pair. This will
        add the class to the <tr> node.
        :param: Callable - the lambda that has access to the result row (dict key: column name, value: column value)
                to produce the class name to be added to the <tr> node of the datatable
        """
        self.get_row_class = getter

    def set_row_data_getter(self, getter: Callable[[dict[str, Any]], dict[str, Any]]) -> None:
        """
        Set the lamda that will return the dict of row data to be used by jquery on the client side.
        The lambda result will be used to update the result row with DT_RowData key value pair. This will
        add the data contained in the dict to the jQuery datatables row using the jQuery data() method
        to set the data, which can also then be used for later retrieval (for example on a click event).
        :param: Callable - the lambda that has access to the result row (dict key: column name, value: column value)
                to produce the datatables row data.
        """
        self.get_row_data = getter

    def set_row_attr_getter(self, getter: Callable[[dict[str, Any]], dict[str, str | int | float]]) -> None:
        """
        Set the lamda that will return the dict of attributes that will be added to the <tr> node of
        the datatable row. The dict keys are used as the attribute keys and the values as the corresponding
        attribute values. This is performed using the jQuery param() method.
        The lambda result will be used update the result row with DT_RowData key value pair.
        :param: Callable - the lambda that has access to the result row (dict key: column name, value: column value)
                to produce the dictionary of <tr> attributes.
        """
        self.get_row_attr = getter

    def run(self, row: dict[str, Any]) -> None:
        if self.get_row_id and self.get_row_id(row):
            row[DTKey.ROW_ID] = self.get_row_id(row)

        if self.get_row_class and self.get_row_class(row):
            row[DTKey.ROW_CLASS] = self.get_row_class(row)

        if self.get_row_data and self.get_row_data(row):
            row[DTKey.ROW_DATA] = self.get_row_data(row)

        if self.get_row_attr and self.get_row_attr(row):
            row[DTKey.ROW_ATTR] = self.get_row_attr(row)


class DTColumnOrder(BaseModel):
    """
    Class holding the parameters for one order criterion from the datatable ajax request
    @see https://www.datatables.net/manual/server-side#Sent-parameters

    :param column_index: int - index of the sort column in the table model
    :param is_asc: bool - sort direction for this column, True -> asc, False -> desc
    """

    column_index: int
    is_asc: bool = True


class DTColumn(BaseModel):
    """
    Class holding the parameters for one column from the datatable ajax request
    @see https://www.datatables.net/manual/server-side#Sent-parameters

    :param index: int - index of the column in the table model
    :param data: str - name of the dict key to get the values for this column from the data list object
    :param name: str - name of the column to reference in datatables jQuery javascript
    :param searchable: bool - whether the column should be searchable or not
    :param orderable: bool - whether the column should be orderable or not
    :param search_value: str - the value for the search filter for this column
    :param search_regex: bool - whether the search filter for this column uses regular expressions
    """

    index: int = -1
    data: str = ''
    name: str = ''
    searchable: bool = True
    orderable: bool = True
    search_value: str = 'None'
    search_regex: bool = False


class DTParams(BaseModel):
    """
    Class holding the query parameters from the datatable ajax request
    @see https://www.datatables.net/manual/server-side#Sent-parameters

    :param draw: int - security id for the ajax request from jQuery datatables
    :param start: int - row to start at, default 0, i.e. offset clause for sql
    :param length: int - number of records returned from the server, default 10, i.e. limit clause for sql
    :param search_value: str | None - global search filter across all searchable columns
    :param search_regex: bool - whether the global search filter uses regular expressions or not
    :param columns: list[DTColumn] - list of column properties
    :param order: list[DTColumnOrder] = list of order criteria
    """

    draw: int = 0
    start: int = 0
    length: int = 10
    search_value: str = ''
    search_regex: bool = False
    columns: list[DTColumn] = []
    order: list[DTColumnOrder] = []
