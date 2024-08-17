from flask_restx import Namespace
from . import resources as res
from utils import add_routes

ns_census = Namespace(
    "Census routes", "Namespace containing standard census handling endpoints"
)

CENSUS_ROUTES = {
    "/census/": res.CensusMaster,
    "/census/<int:id>": res.CensusMaster,
    "/census/upload": res.CensusUpload,
    "/rate": res.RateMaster,
    "/rate/<int:id>": res.RateMaster,
    "/save-age": res.SaveAgeCalc,
}

add_routes(ns_census, CENSUS_ROUTES)
