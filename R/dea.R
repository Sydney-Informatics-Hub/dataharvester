#' Download from Digital Earth Australia
#'
#' Wrapper funtion to get the layers from Digital Earth Australia collections.
#'
#' @details
#'
#' # Layers
#'
#' - `ga_ls_ard_3`: DEA Surface Reflectance (Landsat)
#' - `s2_nrt_granule_nbar_t`: DEA Surface Reflectance (Sentinel-2 Near Real-Time)
#' - `s2_ard_granule_nbar_t`: DEA Surface Reflectance (Sentinel-2)
#' - `ga_ls8c_nbart_gm_cyear_3`: DEA GeoMAD (Landsat 8 OLI-TIRS)
#' - `ga_ls7e_nbart_gm_cyear_3`: DEA GeoMAD (Landsat 7 ETM+)
#' - `ga_ls5t_nbart_gm_cyear_3`: DEA GeoMAD (Landsat 5 TM)
#' - `ga_ls8c_ard_3`: DEA Surface Reflectance (Landsat 8 OLI-TIRS)
#' - `ga_ls7e_ard_3`: DEA Surface Reflectance (Landsat 7 ETM+)
#' - `ga_ls5t_ard_3`: DEA Surface Reflectance (Landsat 5 TM)
#' - `ga_ls8c_ard_provisional_3`: DEA Surface Reflectance (Landsat 8 OLI-TIRS, Provisional)
#' - `ga_ls7e_ard_provisional_3`: DEA Surface Reflectance (Landsat 7 ETM+, Provisional)
#' - `ga_ls_ard_provisional_3`: DEA Surface Reflectance (Landsat, Provisional)
#' - `s2b_nrt_granule_nbar_t`: DEA Surface Reflectance (Sentinel-2B MSI Near Real-Time)
#' - `s2a_nrt_granule_nbar_t`: DEA Surface Reflectance (Sentinel-2A MSI Near Real-Time)
#' - `s2_nrt_provisional_granule_nbar_t`: DEA Surface Reflectance (Sentinel-2, Provisional)
#' - `s2b_nrt_provisional_granule_nbar_t`: DEA Surface Reflectance (Sentinel-2B MSI, Provisional)
#' - `s2a_nrt_provisional_granule_nbar_t`: DEA Surface Reflectance (Sentinel-2A MSI, Provisional)
#' - `s2a_ard_granule_nbar_t`: DEA Surface Reflectance (Sentinel-2A MSI)
#' - `s2b_ard_granule_nbar_t`: DEA Surface Reflectance (Sentinel-2B MSI)
#' - `ga_ls_landcover`: DEA Land Cover Calendar Year (Landsat)
#' - `ga_ls_landcover_descriptors`: DEA Land Cover Environmental Descriptors
#' - `ga_ls_fc_3`: DEA Fractional Cover (Landsat)
#' - `ga_ls_fc_pc_cyear_3`: DEA Fractional Cover Percentiles Calendar Year (Landsat)
#' - `ga_ls_mangrove_cover_cyear_3`: DEA Mangroves (Landsat)
#' - `s2_barest_earth`: GA Barest Earth (Sentinel-2)
#' - `ls8_barest_earth_mosaic`: GA Barest Earth (Landsat 8 OLI/TIRS)
#' - `landsat_barest_earth`: GA Barest Earth (Landsat)
#' - `ga_ls_tcw_percentiles_2`: DEA Wetness Percentiles (Landsat)
#' - `ga_ls_tc_pc_cyear_3`: DEA Tasseled Cap Indices Percentiles Calendar Year (Landsat)
#' - `ga_ls_wo_3`: DEA Water Observations (Landsat)
#' - `ga_ls_wo_fq_myear_3`: DEA Water Observations Multi Year (Landsat)
#' - `ga_ls_wo_fq_cyear_3`: DEA Water Observations Calendar Year (Landsat)
#' - `ga_ls_wo_fq_apr_oct_3`: DEA Water Observations April to October (Landsat)
#' - `ga_ls_wo_fq_nov_mar_3`: DEA Water Observations November to March (Landsat)
#' - `wofs_filtered_summary`: DEA Multi-Year Water Observation Frequency Filtered Statistics (Landsat, DEPRECATED)
#' - `wofs_summary_clear`: DEA Multi-Year Clear Observation Statistics (Landsat, DEPRECATED)
#' - `wofs_summary_wet`: DEA Multi-Year Wet Observation Statistics (Landsat, DEPRECATED)
#' - `Water Observations from Space Statistics`: DEA Multi-Year Water Observation Frequency Statistics (Landsat, DEPRECATED)
#' - `wofs_filtered_summary_confidence`: DEA Multi-Year Water Observation Confidence Statistics (Landsat, DEPRECATED)
#' - `ITEM_V2.0.0`: DEA Intertidal Extents (Landsat)
#' - `ITEM_V2.0.0_Conf`: DEA Intertidal Extents confidence
#' - `NIDEM`: DEA Intertidal Elevation (Landsat)
#' - `high_tide_composite`: DEA High Tide Imagery (Landsat)
#' - `low_tide_composite`: DEA Low Tide Imagery (Landsat)
#' - `ga_s2_ba_provisional_3`: DEA Burnt Area Characteristic Layers (Sentinel 2 Near Real-Time, Provisional)
#' - `alos_displacement`: ALOS Displacement
#' - `alos_velocity`: ALOS Velocity
#' - `envisat_displacement`: ENVISAT Displacement
#' - `envisat_velocity`: ENVISAT Velocity
#' - `radarsat2_displacement`: RADARSAT2 Displacement
#' - `radarsat2_velocity`: RADARSAT2 Velocity
#' - `aster_false_colour`: False Colour Mosaic
#' - `aster_regolith_ratios`: Regolith Ratios
#' - `aster_aloh_group_composition`: AlOH Group Composition
#' - `aster_aloh_group_content`: AlOH Group Content
#' - `aster_feoh_group_content`: FeOH Group Content
#' - `aster_ferric_oxide_composition`: Ferric Oxide Composition
#' - `aster_ferric_oxide_content`: Ferric Oxide Content
#' - `aster_ferrous_iron_content_in_mgoh`: Ferrous Iron Content in MgOH/Carbonate
#' - `aster_ferrous_iron_index`: Ferrous Iron Index
#' - `aster_green_vegetation`: Green Vegetation Content
#' - `aster_gypsum_index`: Gypsum Index
#' - `aster_kaolin_group_index`: Kaolin Group Index
#' - `aster_mgoh_group_composition`: MgOH Group Composition
#' - `aster_mgoh_group_content`: MgOH Group Content
#' - `aster_opaque_index`: Opaque Index
#' - `aster_silica_index`: TIR Silica index
#' - `aster_quartz_index`: TIR Quartz Index
#' - `multi_scale_topographic_position`: Multi-Scale Topographic Position
#' - `weathering_intensity`: Weathering Intensity
#'
#' @param layer `r params(layer)`
#' @param bounding_box `r params(bounding_box)`
#' @param out_path `r params(out_path)`
#' @param date_min `r params(date_min)`
#' @param date_max `r params(date_max)`
#' @param resolution `r params(resolution)`
#' @param crs `r params(crs)`
#' @param format_out Output format, either "GeoTIFF" or "NetCDF". Defaults to
#'   "GeoTIFF"
#'
#' @return a list of filenames (after files have been downloaded or processed)
#' @export
download_dea <- function(layernames,
                         bounding_box,
                         out_path,
                         date_min,
                         date_max,
                         resolution,
                         crs = "EPSG:4326",
                         format_out = "GeoTIFF") {
  # Import module
  dea <- gdh$getdata_dea
  # Run
  out <- dea$get_dea_layers_daterange(
    layernames,
    date_min,
    date_max,
    bounding_box,
    resolution,
    out_path,
    crs,
    format_out
  )
  class(out) <- append(class(out), "rasterPath")
  return(out)
}
