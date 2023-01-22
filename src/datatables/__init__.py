"""Sqlalchemy2-datatables library, provides serverside implementation for jQuery Datatables"""

__version__ = '0.5.4'

from datatables.base import DTDataCallbacks
from datatables.datatable import DataTable

__all__ = ['DataTable', 'DTDataCallbacks']
