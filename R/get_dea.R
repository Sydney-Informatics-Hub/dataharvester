# Deprecated but code is useful (will delete after logtable functions are copied)
.get_dea <- function(x, config = NULL, agg = c("mean", "perc95", "perc5"), ...) {
  # Is object pased on by wrap_config()? If yes, settings can be extracted
  # from this object
  if ("agrefed.wrap" %in% class(x) & is.null(config)) {
    settings <- x$config
  } else if (!is.null(config)) {
    if ("harvester" %in% class(config)) {
      # if config is passed on as an object of class harvester
      settings <- config
    } else if (file.exists(config)) {
      # if config is a path to a yaml file
      settings <- read_yaml(config)
    } else if (is.null(config)) {
      stop("Unable to load configuration from file or object.\n")
    }
  }

  # Check if bounding box is set to NULL or "None". If it is, generate default
  # bounding box values
  if (settings$target_bbox == "None" | is.null(settings$target_bbox)) {
    # Extract long and lat values
    longs <- pull(x$df, settings$colname_lng)
    lats <- pull(x$df, settings$colname_lat)

    # Then, define bounding box to extract data
    boundbox <- c(
      min(longs) - 0.05,
      min(lats) - 0.05,
      max(longs) + 0.05,
      max(lats) + 0.05
    )
  } else {
    boundbox <- settings$target_bbox
  }

  # Run get_dea_layers()
  cli::cli_h1("Farming DEA layers")

  getdata_dea_py <- dd_source_python("getdata_dea", "dataharvestR")
  dea <-
    getdata_dea_py$get_dea_layers(
      layernames = settings$target_sources$DEA$names,
      years = settings$target_dates,
      bbox = boundbox,
      outpath = settings$outpath,
      crs = settings$target_crs,
      format_out = "GEOTIFF",
      verbose = FALSE
    )

  # Aggregate data
  utils_py <- dd_source_python("utils", "dataharvestR")

  # Write to log file

  ## First create temporary yaml file as the update_logtable() function
  ## needs to look at a namespace and it's not easy to recreate it in R
  temp_yaml <- tempfile(fileext = ".yaml")
  yaml::write_yaml(settings, file = temp_yaml)
  settingshandler_py <- dd_source_python("settingshandler", "dataharvestR")
  pyconfig <- settingshandler_py$main(temp_yaml)
  unlink(temp_yaml) # remove temp file when done

  # Then write log
  utils_py <- dd_source_python("utils", "dataharvestR")
  log <-
    utils_py$update_logtable(
      df_log = x$log,
      filenames = slga,
      layernames = settings$target_sources$SLGA$names,
      datasource = "SLGA",
      settings = pyconfig,
      layertitles = list(),
      loginfos = "downloaded"
    )

  # Compile data for output
  out <- list(df = x$df, config = settings, log = log)
  class(out) <- append(class(out), "agrefed.wrap")
  return(invisible(out))
}
