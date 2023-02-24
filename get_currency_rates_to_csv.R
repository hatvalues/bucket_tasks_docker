# Required Packages
packages <- c("XML", "tidyr", "dplyr", "vcdExtra", "stringr", "sets")

# Install if not already
for (p in packages) {
  if (!(require(p, character.only = TRUE))) {
    install.packages(p, dep=TRUE)
    require(p, character.only = TRUE)
  }
}

# set up of country list using web scraping
country_connection <- url("https://www.countries-ofthe-world.com/countries-of-europe.html")
country_page <- readLines(country_connection)
country_table <- readHTMLList(country_page)
countries_of_europe <- c(country_table[[2]], country_table[[3]], country_table[[4]])
countries_of_europe <- countries_of_europe[sapply(countries_of_europe, nchar) > 1]
countries_of_europe[countries_of_europe == "United Kingdom (UK)"] <- "United Kingdom" # inconsitent source

# currency lists
currency_connnection = url("https://www.countries-ofthe-world.com/world-currencies.html")
currency_page <- readLines(currency_connnection)
currency_table <- readHTMLTable(currency_page)
currency_table <- currency_table[[1]]
currencies_of_europe <- currency_table$Currency[match(countries_of_europe, as.character(currency_table$`Country or territory`))]
currency_codes_of_europe <- currency_table$`ISO-4217`[match(countries_of_europe, as.character(currency_table$`Country or territory`))]

# exchange rates
frx_rates <- tibble(
  currency_code = character(),
  from_dollar = numeric(),
  to_dollar = numeric()
)

rates <- set() # dedup lookups e.g. EUR
for (currency_code in currency_codes_of_europe) {
  print(currency_code)
  if (currency_code %e% rates) {
    print(paste(currency_code, ": She done already done had hers's!"))
  } else {
    frx_connection <- url(
      paste0("https://www.xe.com/currencyconverter/convert/?Amount=1&From=USD&To=",
             currency_code
      )
    )
    frx_page <-  readLines(frx_connection)
    frx_table <- readHTMLTable(frx_page)
    from_dollar <- frx_table[[1]][[2]][1]
    from_dollar <- as.numeric(str_replace(from_dollar, paste0(" ", currency_code), ""))
    to_dollar <- frx_table[[2]][[2]][1]
    to_dollar <- as.numeric(str_replace(from_dollar, " USD", ""))
    frx_rates <- rbind(frx_rates,
      tibble::tibble_row(
        currency_code = currency_code,
        from_dollar = from_dollar,
        to_dollar = to_dollar
      )
    )
    rates <- set_union(rates, currency_code)
  }
}

currency_rates_table <- cbind(
  country = countries_of_europe,
  currency = currency_codes_of_europe,
  frx_rates[
    match(
      currency_codes_of_europe,
      frx_rates$currency_code
    ),
      c("from_dollar", "to_dollar")
  ]
)

write.table(
  currency_rates_table,
  sep=",",#
  quote = FALSE,
  file = "C:\\Users\\Crutt\\OneDrive\\Documents\\hatvalues_repo\\bucket_tasks_docker\\files\\currency_rates_table.csv",
  row.names = FALSE,
  col.names = TRUE
)
