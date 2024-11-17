# Leiðbeiningar - Capstone The Reach

Hér má sjá leiðbeiningar vegna Capstone verkefnis frá okkur Erlendri, Ingvari, Þráni og Jakobi. 

## *Um verkefnið*
Þetta verkefni snýst um að safna saman og sýna töluleg gögn um ensku úrvalsdeildina. 
Tilgangurinn með verkefninu er að reyna sína á sem einfaldastan hátt þær tölulegar upplýsingar 
Hægt verður að sjá ýmsa hluti í mælaborðinu en á upphafssíðu mælaborðsins eru upplýsingar um mælaborðið sjálft. 


## Skref 1 - Clone Git rebo
Byrja á því að clone-a Git repo (Ef þú/þið kunnið það ekki koma hér leiðbeiningar um hevrnig það er gert)

## *Clone-a Git rebo í gegnum Git Desktop*
* Fara á *https://github.com/Upplysingaverkfraedi/capstone-thereach* 
* Næst skal halda sig á main branch (EKKI FARA INN Á NEITT ANNAÐ BRANCH)
* Næst skal smella á *Code* takkann sem er grænn
* Þar skal velja *Open with GitHub Desktop*
* Við þetta opnast GitHub Desktop
  * Ef desktop var þegar opið er hægt að velja *Leave changes* á því branchi sem síðast var verið að vinna með
* Næst Skal smella á *Open the repository in your external editor* en þar ætti að vera hnappurinn *Open in Visual Studio Code*

Við þetta á þá verið að búa að clone-a allt og opna main branch í VScode. 

## Skref 2 - Sækja öll nauðsynleg skjöl og forrit
Það sem þarf til að fá upp endanlegt mælaborð eru eftirfarandi skjöl og forrit:
* *Database.py*
* *Games_season19-20.csv*
* *Premier League Player Stats.csv*
* *stadiums-with-GPS-coordinates.csv*
* *CodeForShiny.rmd*
* Logos mappan

Þetta ætti allt að koma þegar það er clone-að Git rebo en ef ekki 
þá er hægt að skoða inn á main branch öll skjölin og hlaða þeim beint niður í tölvuna ykkar og færa það inn í rétta möppu. 

## Skref 3 - Passa að allt sé á réttum stað
Áður en farið er að keyra eitthvað þarf að passa **tvennt** 
* Búa til **data** möppu (Þetta er gert til að geyma öll csv skjölin sem myndast við keyrsluna svo þau séu ekki fyrir)
  * Hægt er að búa til hana beint í vscode
* Allir file-ar séu beint undir CAPSTONE-THEREACH eða sambærilegt en ekki data, s.s. undir sömu möppunni/directory. 
  * ATH: Ef csv skrár eru undir annari möppu þá þarf að færa þær. 


## Skref 4 - Búa til gagnagrunn
Til að búa til gagnagrunninn þarf einfaldlega að keyra *Database.py*
* Opna Terminal
* Slá inn *python Database.py --season "2010-2024" --debug*
  * Hér er hægt að velja hvaða tímabil(season) á að sækja
  * Við það að hafa 2010-2024 eru sótt öll tímabil innan þess ramma

Við það að keyra *Database.py* er gagngrunnurinn klár.
Hann hefur:
* Sett inn allar þrjár csv skrárnar
* Tekið upplýsingar frá FotMob.com fótbolta síðunni
* Hreinsað gögnin


## Skref 5 - Keyra upp mælaborðið
Opna þarf fyrst beint úr file explorer (Finder fyrir apple fólk) R-skjalið
* CodeForShiny.rmd

# ATH: Passaðu að downloada í console eftirfarandi pökkum með skipun!!
Þegar opnað er R-studio með CodeForShiny.rmd á að koma upp valmöguleiki að install alla pakka sem þarf.
Ef það kemur ekki er hægt að slá eftirfarandi inn í Console til að hlaða þeim öllum 
```bash
install.packages("tidyverse")
install.packages("rvest")
install.packages("dplyr")
install.packages("DBI")
install.packages("RSQLite")
install.packages("shiny")
install.packages("ggplot2")
install.packages("plotly")
install.packages("shinyjs")
install.packages("shinydashboard")
install.packages("DT")
install.packages("sf")
install.packages("leaflet")
install.packages("ggimage")
```

Þegar allir pakkar(packages) eru uppsettir þarf einfaldlega að:
* Keyra hvern r-chunk frá toppi og niður

Það eru aðeins 8 r-chunks sem þarf að keyra:
* Lína 8
* Lína 14
* Lína 33
* Lína 46
* Lína 62
* Lína 71
* Lína 253
* Lína 963 

Síðasti r-chunk er: 
```{r}
shinyApp(ui, server)
```

og með því að keyra hann ætti vefsíðan/mælaborðið að opnast. 
Á upphafssíðunni koma fram upplýsingar um mælaborðið. 
