# tennis-court-reservation-system
Tenniskenttien varausjärjestelmä, jossa asiakkaat voivat selailla eri vuoroja, varata kenttiä, peruuttaa varauksen ja takistella omaa varaushistoriaa. Asiakas voi luoda oman tunnuksen, kirjautua sisään ja ulos, sekä muokata omia tietojaan. Kentän varaamiseen vaaditaan käyttäjätunnus.

# SOVELLUS LÖYTYY MAIN BRANCHISTA.

# Windows ohjeet sovelluksen kokeilemiseen:
1. Avaa terminaali ja siirry kansioon, johon haluat kloonata repositorion ja sitten kloona repositorio sinne.
2. Siirry juurikansioon
4. Luo .env-tiedosto ja määritä sen sisältö näillä:
   DATABASE_URL=postgresql://username:password@localhost:5432/tennis_reservation_system
   SECRET_KEY=salainen_avain_123
5. Aktivoi virtuaaliympäristö ja asenna riippuvuudet:
   python -m venv venv
   venv\Scripts\activate
6. Asenna sovelluksen riippuvuudet:
   pip install -r requirements.txt
7. Määritä vielä tietokannan skeema:
   psql < schema.sql
8. käynnistää sovellus:
   flask run

# Linux ohjeet sovelluksen kokeilemiseen
1. Avaa terminaali ja siirry kansioon, johon haluat kloonata repositorion ja sitten kloona repositorio sinne.
2. Siirry juurikansioon
4. Luo .env-tiedosto ja määritä sen sisältö näillä:
   DATABASE_URL=postgresql://username:password@localhost:5432/tennis_reservation_system
   SECRET_KEY=salainen_avain_123
5. Aktivoi virtuaaliympäristö ja asenna riippuvuudet:
   python3 -m venv venv
   source venv/bin/activate
6. Asenna sovelluksen riippuvuudet:
   pip install -r requirements.txt
7. Määritä vielä tietokannan skeema:
   psql < schema.sql
8. käynnistää sovellus:
   flask run

# Sovelluksen toiminnot
Tällä hetkellä sovelluksessa voi tarkastella aukioloaikoja ja hinnastoa. Voit myös luoda tunnuksen ja kirjautua sisään. Tietokannassa on valmis asiakas (sposti: a@a, salasana: a) valmiina, tai voit luoda oman käyttäjän ja kirjautua sillä sisään. Sisäänkirjautuneena näet "omat tiedot" napista omat tietosi ja varauksesi, joita voit myös muokata. "Omat tiedot" kohdasta voi myös kirjautua ulos.
