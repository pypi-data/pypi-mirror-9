# -*- coding: utf-8 -*-
__author__ = 'Alex Dzul'
from pyql.geo.generics import GenericGeoPlace
from pyql.interface import YQLConector


__all__ = ('Ocean', )

YQL_TABLE = "geo.oceans"


class Ocean(GenericGeoPlace):

    @staticmethod
    def get(**kwargs):
        """
        Realiza una consulta a la base de datos de Yahoo utilizando YQL.
        El valor retornado un solo elemento. Si la consulta retorna más entonces
        se presentará un error de múltiples resultados encontrados.
        """
        connect = YQLConector()
        query = connect.make_query(YQL_TABLE, **kwargs)
        response = connect.request(query)
        return Ocean.generic_get(response)

    @staticmethod
    def filter(**kwargs):
        """
        Realiza una consulta a la base de datos de Yahoo utilizando YQL.
        El valor retornado siempre será una lista de objetos tipo "Oceans"
        """
        connect = YQLConector()
        query = connect.make_query(YQL_TABLE, **kwargs)
        response = connect.request(query)
        return Ocean.generic_filter(response)