import logging
import random
import re
from typing import Any

from sqlalchemy import FromClause, Result, and_, asc, desc, func, or_, select
from sqlalchemy.future import Engine
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement, KeyedColumnElement
from sqlalchemy.sql.selectable import Select, Subquery

from datatables.base import DTColumn, DTColumnOrder, DTDataCallbacks, DTParams


class DataTable:
    """
    Sqlalchemy ORM-compatible data table class.
    See https://www.datatables.net/manual/server-side#API

    :param engine: Engine -  sqlalchemy database engine
    :param table: table: FromClause - sqlalchemy FromClause
    :param column_names: list[str] - table column names to display in the datatable, used for projection in sql
    :attr params: DTParams - parsed request parameters to use for result filtering, projection, sorting and paging
    :attr recordsTotal: int -  the total number of records available in this model/table
    :attr recordsFiltered: int - the number of records for the filtered result (before pagination)
    :attr data: list[dict] - the list of data objects sent to the datatable
    :attr error: str -  if there was an error with data retrieval, this the error message will be sent instead
    """

    callbacks: DTDataCallbacks | None
    engine: Engine
    table: FromClause
    column_names: list[str]
    params: DTParams
    records_total: int = 0
    records_filtered: int = 0
    data: list[dict[str, Any]] = []
    error: str | None = None

    def __init__(
        self,
        request_params: dict[str, Any],
        table: FromClause,
        column_names: list[str],
        engine: Engine,
        callbacks: DTDataCallbacks | None = None,
    ):
        self.table = table
        self.column_names = column_names
        self.engine = engine
        self.callbacks = callbacks
        logging.info(f'initialize DataTable for {self.table}')
        try:
            self.run(request_params)
        except Exception as exc:
            self.error = str(exc)

    @staticmethod
    def _parse_order(request_params: dict[str, Any]) -> list[DTColumnOrder]:
        """Parse the order[index][*] parameters"""
        order: list[DTColumnOrder] = []
        order_pattern = re.compile(r'order\[(.*?)]\[column]')
        order_params: dict[str, Any] = {k: v for k, v in request_params.items() if order_pattern.match(k)}

        for i in range(len(order_params)):
            dt_column_order: DTColumnOrder = DTColumnOrder(
                column_index=request_params[f'order[{i}][column]'],
                is_asc=request_params[f'order[{i}][dir]'] == 'asc',
            )
            order.append(dt_column_order)
        return order

    @staticmethod
    def _parse_columns(request_params: dict[str, Any]) -> list[DTColumn]:
        """Parse the column[index][*] parameters"""
        columns: list[DTColumn] = []
        data_pattern = re.compile(r'columns\[(.*?)]\[data]')
        # Extract only the keys of type columns[i][data] from the params
        data_param: dict[str, Any] = {k: v for k, v in request_params.items() if data_pattern.match(k)}

        for i in range(len(data_param)):
            column: DTColumn = DTColumn(
                index=i,
                data=data_param.get(f'columns[{i}][data]'),
                name=request_params.get(f'columns[{i}][name]'),
                searchable=request_params.get(f'columns[{i}][searchable]') == 'true',
                orderable=request_params.get(f'columns[{i}][orderable]') == 'true',
                search_value=request_params.get(f'columns[{i}][search][value]'),
                search_regex=request_params.get(f'columns[{i}][search][regex]') == 'true',
            )
            columns.append(column)
        return columns

    @staticmethod
    def _parse_params(request_params: dict[str, Any]) -> DTParams:
        """Parse the request (query) parameters"""
        params = DTParams()
        draw: int = int(request_params.get('draw', 0))
        params.draw = random.randint(1, 1000) if draw == 0 else draw
        params.start = int(request_params.get('start', 0))
        params.length = int(request_params.get('length', -1))
        params.search_value = request_params.get('search[value]', '')
        params.search_regex = request_params.get('search[regex]') == 'true'
        params.columns = DataTable._parse_columns(request_params)
        params.order = DataTable._parse_order(request_params)
        logging.info(f'params: {params}')
        return params

    def _get_records_total(self, session: Session) -> int:
        # total record count before filtering
        result: int | None = session.scalar(select(func.count()).select_from(self.table))
        return 0 if result is None else result

    @staticmethod
    def _get_records_filtered(session: Session, subquery: Subquery) -> int:
        result: int | None = session.scalar(select(func.count()).select_from(subquery))
        return 0 if result is None else result

    def _get_table_column_by_index(self, index: int) -> KeyedColumnElement[Any]:
        name: str = self.column_names[index]
        return self.table.columns[name]

    def _add_order_criteria(self, stmt: Select[Any]) -> Select[Any]:
        """Add order by criteria to select statement"""
        for order in self.params.order:
            column: KeyedColumnElement[Any] = self._get_table_column_by_index(order.column_index)
            stmt = stmt.order_by(asc(column)) if order.is_asc else stmt.order_by(desc(column))
        return stmt

    def _add_global_search_criterion(self, stmt: Select[Any]) -> Select[Any]:
        """Add global search filter across all searchable columns to select statement"""
        expressions: list[ColumnElement[Any]] = []
        for dt_col in self.params.columns:
            if dt_col.searchable:
                column: KeyedColumnElement[Any] = self._get_table_column_by_index(dt_col.index)
                col_element: ColumnElement[Any]
                if self.params.search_regex:
                    regex: str = self.params.search_value
                    col_element = column.regexp_match(regex)
                else:
                    col_element = column.like(f'%{self.params.search_value}%')
                expressions.append(col_element)
        return stmt.where(or_(*expressions)) if len(expressions) > 0 else stmt

    def _add_column_search_criteria(self, stmt: Select[Any]) -> Select[Any]:
        """add the individual column filters to select statement"""
        expressions: list[ColumnElement[Any]] = []
        for dt_col in self.params.columns:
            if dt_col.search_value:
                column: KeyedColumnElement[Any] = self._get_table_column_by_index(dt_col.index)
                if self.params.search_regex:
                    col_element = column.regexp_match(dt_col.search_value)
                else:
                    col_element = column.like(f'%{dt_col.search_value}%')
                expressions.append(col_element)
        return stmt.where(and_(*expressions)) if len(expressions) > 0 else stmt

    def _built_select_statement(self) -> Select[Any]:
        stmt: Select[Any] = select().select_from(self.table)
        for name in self.column_names:
            stmt = stmt.add_columns(self.table.columns[name])
        if self.params.search_value:
            stmt = self._add_global_search_criterion(stmt)
        stmt = self._add_column_search_criteria(stmt)
        stmt = self._add_order_criteria(stmt)
        return stmt

    def _get_data(self, session: Session, stmt: Select[Any]) -> list[dict[str, Any]]:
        """Get the data from the database"""
        # adding pagination by page (offset/start) and page size (limit/length)
        stmt = stmt.offset(self.params.start).limit(self.params.length)
        logging.info(f'stmt: {stmt.compile()}')
        result: Result[Any] = session.execute(stmt)
        # create a dictionary that maps the result of the query to a list
        # data: list[dict[str, Any]] = [{k: v for k, v in zip(self.column_names, row)} for row in result.all()]
        data: list[dict[str, Any]] = []
        for row in result.all():
            result_row: dict[str, Any] = {k: v for k, v in zip(self.column_names, row, strict=True)}
            if self.callbacks:
                self.callbacks.run(result_row)
            data.append(result_row)
        return data

    def run(self, request_params: dict[str, Any]) -> None:
        self.params = self._parse_params(request_params)
        with Session(self.engine) as session:
            # get total record count from the table
            self.records_total = self._get_records_total(session)
            # get the select statement with all the search and order criteria
            stmt: Select[Any] = self._built_select_statement()
            # get the filtered record count from the statement that will also produce the data
            self.records_filtered = self._get_records_filtered(session, stmt.subquery())
            # get the filtered records from the database
            self.data = self._get_data(session, stmt)

    def output_result(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            'start': self.params.start,
            'length': self.params.length,
            'draw': self.params.draw,
            'recordsTotal': self.records_total,
            'recordsFiltered': self.records_filtered,
            'data': self.data,
        }
        return result
