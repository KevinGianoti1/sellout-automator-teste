
import streamlit_authenticator as stauth

# Lista de nomes, usernames, perfis, empresas e apelidos
user_data = [
    ("admin", "Administrador", "000", "Admin", "MF Ferramentas", "Admin"),
    ("agnes", "Agnes", "001", "Vendedora", "Maxi Force", "Agnes (Frô)"),
    ("camila", "Camila", "002", "Vendedora", "Maxi Force", "Ca"),
    ("fernanda", "Fernanda", "003", "Vendedora", "Maxi Force", "Fê"),
    ("ana", "Ana Paula", "004", "Vendedora", "Maxi Force", "Ana"),
    ("wellington", "Wellington", "005", "Vendedor", "Maxi Force", "Wellington"),
    ("bruno", "Bruno", "006", "Vendedor", "Pyramid", "BB"),
    ("vinicius", "Vinicius", "007", "Vendedor", "Pyramid", "Vini Boy"),
    ("derec", "Derec", "008", "Vendedor", "Pyramid", "Derec"),
    ("matheus", "Matheus", "009", "Vendedor", "Pyramid", "Matheus")
]

# Senhas criptografadas (pré-geradas para cada código 000-009)
hashed_passwords = [
    "$2b$12$0m5jof1vRQ0m1IoEOIRIlObpF/vyo6fhOxsRXQpBK1wCK4nKp/R4e",  # 000
    "$2b$12$EGKjoghdEKtxM8U9Z44vNOXH0M8yYwlC66OxiqSL3X.6S8tyVfxPa",
    "$2b$12$tcTPzM49/0NKBuXLNDsQJO3ZB.EUDV5nU3XUUXGArFGVghKbCSN0e",
    "$2b$12$olNCpq3TLL26xfDxxax.3OkhFV92MnZd4U5Yv4H0eUZZ8xQn9eRdu",
    "$2b$12$yRc0nLPhR9ZBhDnXzOQrfOmSm/1/OiPYPxKo8VL9ENvTfQAGb0kLC",
    "$2b$12$Gg5RLyOEXeYtFxqvK0aZ9uP1uRAZhOV3MiU1I24nxUuJmHZp9OJ4G",
    "$2b$12$gEYFezX9xal0eDH3qD0AP.N2CEYpn8wRxAuWY77NB4K3lSYDhG49q",
    "$2b$12$ydCeFYWhm5J6sp4cpnkh7um.B8IS5GOevkakdXh8zvAoa3iEmkg8O",
    "$2b$12$TcVOqHEbmS9UUXx/G0orBe34cd7s/hFOxInGNE0UB0VV56Ctj4TQm",
    "$2b$12$YECXU9TKMG4YUvHsW2SrSOHDa7aOqz63ZJm8MSv/PPKtU/.tTeOS6"
]

# Monta o dicionário de credenciais completo
credentials = {
    "usernames": {
        username: {
            "name": name,
            "password": hashed,
            "perfil": perfil,
            "empresa": empresa,
            "apelido": apelido
        }
        for (username, name, _, perfil, empresa, apelido), hashed in zip(user_data, hashed_passwords)
    }
}

import streamlit_authenticator as stauth

# Lista de nomes, usernames, perfis, empresas e apelidos
user_data = [
    ("admin", "Administrador", "000", "Admin", "MF Ferramentas", "Admin"),
    ("agnes", "Agnes", "001", "Vendedora", "Maxi Force", "Agnes (Frô)"),
    ("camila", "Camila", "002", "Vendedora", "Maxi Force", "Ca"),
    ("fernanda", "Fernanda", "003", "Vendedora", "Maxi Force", "Fê"),
    ("ana", "Ana Paula", "004", "Vendedora", "Maxi Force", "Ana"),
    ("wellington", "Wellington", "005", "Vendedor", "Maxi Force", "Wellington"),
    ("bruno", "Bruno", "006", "Vendedor", "Pyramid", "BB"),
    ("vinicius", "Vinicius", "007", "Vendedor", "Pyramid", "Vini Boy"),
    ("derec", "Derec", "008", "Vendedor", "Pyramid", "Derec"),
    ("matheus", "Matheus", "009", "Vendedor", "Pyramid", "Matheus")
]

# Senhas criptografadas (pré-geradas para cada código 000-009)
hashed_passwords = [
    "$2b$12$0m5jof1vRQ0m1IoEOIRIlObpF/vyo6fhOxsRXQpBK1wCK4nKp/R4e",  # 000
    "$2b$12$EGKjoghdEKtxM8U9Z44vNOXH0M8yYwlC66OxiqSL3X.6S8tyVfxPa",
    "$2b$12$tcTPzM49/0NKBuXLNDsQJO3ZB.EUDV5nU3XUUXGArFGVghKbCSN0e",
    "$2b$12$olNCpq3TLL26xfDxxax.3OkhFV92MnZd4U5Yv4H0eUZZ8xQn9eRdu",
    "$2b$12$yRc0nLPhR9ZBhDnXzOQrfOmSm/1/OiPYPxKo8VL9ENvTfQAGb0kLC",
    "$2b$12$Gg5RLyOEXeYtFxqvK0aZ9uP1uRAZhOV3MiU1I24nxUuJmHZp9OJ4G",
    "$2b$12$gEYFezX9xal0eDH3qD0AP.N2CEYpn8wRxAuWY77NB4K3lSYDhG49q",
    "$2b$12$ydCeFYWhm5J6sp4cpnkh7um.B8IS5GOevkakdXh8zvAoa3iEmkg8O",
    "$2b$12$TcVOqHEbmS9UUXx/G0orBe34cd7s/hFOxInGNE0UB0VV56Ctj4TQm",
    "$2b$12$YECXU9TKMG4YUvHsW2SrSOHDa7aOqz63ZJm8MSv/PPKtU/.tTeOS6"
]

# Monta o dicionário de credenciais completo
credentials = {
    "usernames": {
        username: {
            "name": name,
            "password": hashed,
            "perfil": perfil,
            "empresa": empresa,
            "apelido": apelido
        }
        for (username, name, _, perfil, empresa, apelido), hashed in zip(user_data, hashed_passwords)
    }
}

