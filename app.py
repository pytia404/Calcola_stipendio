from flask import Flask, render_template, request

app = Flask(__name__)



# ALIQUOTE INPS

ALIQUOTA_INPS = {
    "indeterminato": 0.0919,
    "apprendistato": 0.0584,
}

# CALCOLO CONTRIBUTI INPS

def calcola_inps(ral, tipo_contratto):
    aliquota = ALIQUOTA_INPS[tipo_contratto]
    return ral * aliquota


# CALCOLO IRPEF

def calcola_irpef(imponibile):
    """
    IRPEF progressiva:

    fino a 28.000 €       -> 23%
    da 28.000 a 50.000 €  -> 35%
    oltre 50.000 €        -> 43%
    """

    irpef = 0

    # Primo scaglione
    primo_scaglione = min(imponibile, 28000)
    irpef += primo_scaglione * 0.23

    # Secondo scaglione
    if imponibile > 28000:
        secondo_scaglione = min(imponibile, 50000) - 28000
        irpef += secondo_scaglione * 0.35

    # Terzo scaglione
    if imponibile > 50000:
        terzo_scaglione = imponibile - 50000
        irpef += terzo_scaglione * 0.43

    return irpef

# CALCOLO ADDIZIONALE PIEMONTE (assunzione)


def calcola_addizionale_piemonte(imponibile):
    """
    Addizionale regionale Piemonte - anno 2026

    fino a 15.000 €              -> 1,62%
    oltre 15.000 fino a 28.000 € -> 2,68%
    oltre 28.000 fino a 50.000 € -> 3,31%
    oltre 50.000 €               -> 3,33%
    """

    addizionale = 0

    # Primo scaglione
    primo_scaglione = min(imponibile, 15000)
    addizionale += primo_scaglione * 0.0162

    # Secondo scaglione
    if imponibile > 15000:
        secondo_scaglione = min(imponibile, 28000) - 15000
        addizionale += secondo_scaglione * 0.0268

    # Terzo scaglione
    if imponibile > 28000:
        terzo_scaglione = min(imponibile, 50000) - 28000
        addizionale += terzo_scaglione * 0.0331

    # Quarto scaglione
    if imponibile > 50000:
        quarto_scaglione = imponibile - 50000
        addizionale += quarto_scaglione * 0.0333

    return addizionale


# CALCOLO COMPLESSIVO


def calcola_stipendio(
    ral,
    tipo_contratto,
    mensilita,
    welfare_annuo
):

    # 1. INPS
    contributi_inps = calcola_inps(
        ral,
        tipo_contratto
    )

    # 2. Imponibile fiscale
    imponibile_fiscale = ral - contributi_inps

    # 3. IRPEF
    irpef = calcola_irpef(
        imponibile_fiscale
    )

    # 4. Addizionale regionale Piemonte
    addizionale_regionale = calcola_addizionale_piemonte(
        imponibile_fiscale
    )

    # 5. Netto derivante dallo stipendio
    netto_annuale = (
        ral
        - contributi_inps
        - irpef
        - addizionale_regionale
    )

    # 6. Netto medio per mensilità
    netto_mensile = netto_annuale / mensilita

    # 7. Welfare ricevuto fuori dalla busta paga
    totale_annuo = netto_annuale + welfare_annuo

    # 8. Valore medio mensile comprensivo del welfare
    valore_medio_mensile = totale_annuo / 12

    return {
        "ral": ral,
        "contributi_inps": contributi_inps,
        "imponibile_fiscale": imponibile_fiscale,
        "irpef": irpef,
        "addizionale_regionale": addizionale_regionale,
        "netto_annuale": netto_annuale,
        "netto_mensile": netto_mensile,
        "welfare_annuo": welfare_annuo,
        "totale_annuo": totale_annuo,
        "valore_medio_mensile": valore_medio_mensile,
    }


# PAGINA PRINCIPALE


@app.route("/", methods=["GET", "POST"])
def index():

    risultato = None

    if request.method == "POST":

        ral = float(
            request.form["ral"]
        )

        tipo_contratto = request.form[
            "tipo_contratto"
        ]

        mensilita = int(
            request.form["mensilita"]
        )

        welfare_annuo = float(
            request.form["welfare_annuo"]
        )

        risultato = calcola_stipendio(
            ral=ral,
            tipo_contratto=tipo_contratto,
            mensilita=mensilita,
            welfare_annuo=welfare_annuo
        )

        risultato["tipo_contratto"] = (
            tipo_contratto
        )

        risultato["mensilita"] = (
            mensilita
        )

    return render_template(
        "index.html",
        risultato=risultato
    )


if __name__ == "__main__":
    app.run(debug=True)