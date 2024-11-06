
# Ef þú ert ekki núþegar með pakka sem vantar til að keyra kóða# install.packages("tidyverse")
# install.packages("sf")
# install.packages("leaflet")
# install.packages("RSQLite")
library(tidyverse)   
library(sf)          
library(leaflet)   
library(RSQLite)  

# Tengjast gagnagrunni, breyta path file eftir því hvar þú geymir premier league gagnagrunninn
con <- dbConnect(RSQLite::SQLite(), "/Users/ingvaratliaudunarson/Documents/GitHub/capstone-thereach/premier_league.db")

# Sækja gögn frá db og setja í nýja töflu sem hægt er að vinna úr
Stadiums_data <- dbGetQuery(con, "SELECT Team, FDCOUK, City, Stadium, Capacity, Latitude, Longitude, Country FROM Stadiums")

# Aftengjast db
dbDisconnect(con)

# Setja inn logo url í töflu, breyta path file eftir því hvar logos folderinn er staðsettur í þinni tölvu
Stadiums_data <- Stadiums_data %>%
  mutate(Logo_url = paste0("/Users/ingvaratliaudunarson/Desktop/Skolinn/upplysingaverk/Logos/", str_replace_all(Team, " ", "_"), ".png"))

# Breyta í Sf fyrir leaflet
Location_data <- st_as_sf(Stadiums_data, coords = c("Longitude", "Latitude"), crs = 4326)

# Búa til kort
leaflet() %>%
  addTiles() %>%
  
  addMarkers(data = Location_data,
             lng = ~st_coordinates(geometry)[, 1],
             lat = ~st_coordinates(geometry)[, 2],
             icon = ~icons(iconUrl = Logo_url, iconWidth = 30, iconHeight = 30),
             popup = ~paste("<b>Team:</b>", Team, "<br><b>Stadium:</b>", Stadium, "<br><b>City:</b>", City, "<br><b>Capacity:</b>", Capacity))

# Ef þú ert ekki núþegar með pakka sem vantar til að keyra kóða
# install.packages("tidyverse")
# install.packages("ggimage")
library(tidyverse)
library(ggimage)

# búa til graf
stadiums_sorted <- Stadiums_data %>%
  arrange(desc(Capacity))

# Setja inn myndir ad liðum í stað stöpla
ggplot(stadiums_sorted, aes(x = reorder(Stadium, Capacity), y = Capacity)) +
  geom_image(aes(image = Logo_url), size = 0.05, by = "width") + 
  coord_flip() +
  labs(title = "Stærð valla í Ensku Úrvalsdeildinni (2019/2020 Season)",
       x = "Stærð (fjöldi sæta)",
       y = "Völlur") +
  theme_minimal() +
  theme(plot.title = element_text(hjust = 0.5))
