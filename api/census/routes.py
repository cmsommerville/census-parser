from flask_restx import Namespace
from . import resources as res
from utils import add_routes

ns_census = Namespace(
    "Census routes", "Namespace containing standard census handling endpoints"
)

CENSUS_ROUTES = {
    "/census/": res.CRUDCensusMaster,
    "/census/<int:id>": res.CRUDCensusMaster,
    "/census/<int:id>/details": res.CRUDCensusDetailList,
    "/census/<int:id>/stats": res.CensusStats,
    "/census/upload": res.CensusUpload,
    "/census/parse": res.CensusParser,
    "/rates": res.CRUDRateMaster,
    "/rates/upload": res.RateUpload,
    "/rates/<int:id>": res.CRUDRateMaster,
    "/save-age": res.SaveAgeCalc,
    "/dd/census": res.CRUDCensusMasterDropdownList,
    "/dd/rates": res.CRUDRateMasterDropdownList,
}

add_routes(ns_census, CENSUS_ROUTES)
