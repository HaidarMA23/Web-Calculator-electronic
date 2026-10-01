from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


# =========================================================
# DATA KODE WARNA RESISTOR
# =========================================================

COLOR_VALUES = {
    "black": 0,
    "brown": 1,
    "red": 2,
    "orange": 3,
    "yellow": 4,
    "green": 5,
    "blue": 6,
    "violet": 7,
    "gray": 8,
    "white": 9
}

COLOR_MULTIPLIER = {
    "black": 1,
    "brown": 10,
    "red": 100,
    "orange": 1000,
    "yellow": 10000,
    "green": 100000,
    "blue": 1000000,
    "violet": 10000000,
    "gray": 100000000,
    "white": 1000000000,
    "gold": 0.1,
    "silver": 0.01
}

COLOR_TOLERANCE = {
    "brown": 1,
    "red": 2,
    "green": 0.5,
    "blue": 0.25,
    "violet": 0.1,
    "gray": 0.05,
    "gold": 5,
    "silver": 10
}


# =========================================================
# FORMAT NILAI
# =========================================================

def format_resistance(value):

    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.3f} GΩ"

    if value >= 1_000_000:
        return f"{value / 1_000_000:.3f} MΩ"

    if value >= 1_000:
        return f"{value / 1_000:.3f} kΩ"

    return f"{value:.3f} Ω"


def format_capacitance(value):

    if value >= 1:
        return f"{value:.6f} F"

    if value >= 1e-3:
        return f"{value * 1e3:.6f} mF"

    if value >= 1e-6:
        return f"{value * 1e6:.6f} µF"

    if value >= 1e-9:
        return f"{value * 1e9:.6f} nF"

    return f"{value * 1e12:.6f} pF"


# =========================================================
# KONVERSI SATUAN
# =========================================================

PREFIX = {
    "G": 1e9,
    "M": 1e6,
    "k": 1e3,
    "": 1,
    "m": 1e-3,
    "u": 1e-6,
    "n": 1e-9,
    "p": 1e-12
}

PREFIX_SYMBOL = {
    "G": "G",
    "M": "M",
    "k": "k",
    "": "",
    "m": "m",
    "u": "µ",
    "n": "n",
    "p": "p"
}

UNIT_NAMES = {
    "ohm": "Ω",
    "farad": "F",
    "volt": "V",
    "ampere": "A",
    "watt": "W",
    "henry": "H"
}


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# CALCULATOR
# =========================================================

@app.route("/calculate", methods=["POST"])
def calculate():

    calculator = request.form.get("calculator")

    try:

        # =================================================
        # 1. HUKUM OHM
        # =================================================

        if calculator == "ohm":

            mode = request.form.get("ohm_mode")

            voltage = request.form.get("voltage")
            current = request.form.get("current")
            resistance = request.form.get("resistance")

            # Menghitung arus
            # I = V / R

            if mode == "current":

                voltage = float(voltage)
                resistance = float(resistance)

                if voltage < 0:
                    return jsonify({
                        "success": False,
                        "message": "Tegangan tidak boleh negatif."
                    })

                if resistance <= 0:
                    return jsonify({
                        "success": False,
                        "message": "Resistansi harus lebih dari 0 Ω."
                    })

                result = voltage / resistance

                return jsonify({
                    "success": True,
                    "result": (
                        "Rumus: I = V / R"
                        f"<br><strong>I = {result:.4f} A</strong>"
                    )
                })

            # Menghitung tegangan
            # V = I × R

            elif mode == "voltage":

                current = float(current)
                resistance = float(resistance)

                if current < 0:
                    return jsonify({
                        "success": False,
                        "message": "Arus tidak boleh negatif."
                    })

                if resistance <= 0:
                    return jsonify({
                        "success": False,
                        "message": "Resistansi harus lebih dari 0 Ω."
                    })

                result = current * resistance

                return jsonify({
                    "success": True,
                    "result": (
                        "Rumus: V = I × R"
                        f"<br><strong>V = {result:.4f} V</strong>"
                    )
                })

            # Menghitung resistansi
            # R = V / I

            elif mode == "resistance":

                voltage = float(voltage)
                current = float(current)

                if voltage < 0:
                    return jsonify({
                        "success": False,
                        "message": "Tegangan tidak boleh negatif."
                    })

                if current <= 0:
                    return jsonify({
                        "success": False,
                        "message": "Arus harus lebih dari 0 A."
                    })

                result = voltage / current

                return jsonify({
                    "success": True,
                    "result": (
                        "Rumus: R = V / I"
                        f"<br><strong>R = "
                        f"{format_resistance(result)}</strong>"
                    )
                })

            return jsonify({
                "success": False,
                "message": "Pilih besaran yang ingin dihitung."
            })


        # =================================================
        # 2. DAYA LISTRIK
        # P = V × I
        # =================================================

        elif calculator == "power":

            voltage = float(
                request.form.get("voltage")
            )

            current = float(
                request.form.get("current")
            )

            if voltage < 0 or current < 0:
                return jsonify({
                    "success": False,
                    "message": "Nilai tidak boleh negatif."
                })

            power = voltage * current

            return jsonify({
                "success": True,
                "result": (
                    "Rumus: P = V × I"
                    f"<br><strong>P = {power:.4f} W</strong>"
                )
            })


        # =================================================
        # 3. RESISTOR SERI
        # =================================================

        elif calculator == "series":

            count = int(
                request.form.get(
                    "resistor_count",
                    3
                )
            )

            resistors = []

            for i in range(1, count + 1):

                value = float(
                    request.form.get(f"r{i}")
                )

                if value < 0:
                    return jsonify({
                        "success": False,
                        "message": "Resistansi tidak boleh negatif."
                    })

                resistors.append(value)

            total = sum(resistors)

            return jsonify({
                "success": True,
                "result": (
                    "Rumus: Rt = R1 + R2 + ... + Rn"
                    f"<br><strong>Rt = "
                    f"{format_resistance(total)}</strong>"
                )
            })


        # =================================================
        # 4. RESISTOR PARALEL
        # =================================================

        elif calculator == "parallel":

            count = int(
                request.form.get(
                    "resistor_count",
                    3
                )
            )

            resistors = []

            for i in range(1, count + 1):

                value = float(
                    request.form.get(f"r{i}")
                )

                if value <= 0:
                    return jsonify({
                        "success": False,
                        "message": (
                            "Semua resistansi harus "
                            "lebih dari 0 Ω."
                        )
                    })

                resistors.append(value)

            inverse_total = sum(
                1 / resistor
                for resistor in resistors
            )

            total = 1 / inverse_total

            return jsonify({
                "success": True,
                "result": (
                    "Rumus: 1/Rt = 1/R1 + 1/R2 + ... + 1/Rn"
                    f"<br><strong>Rt = "
                    f"{format_resistance(total)}</strong>"
                )
            })


        # =================================================
        # 5. RESISTOR LED
        # =================================================

        elif calculator == "led":

            supply = float(
                request.form.get("supply")
            )

            led_voltage = float(
                request.form.get("led_voltage")
            )

            current_ma = float(
                request.form.get("led_current")
            )

            current_a = current_ma / 1000

            if supply < 0 or led_voltage < 0:
                return jsonify({
                    "success": False,
                    "message": "Tegangan tidak boleh negatif."
                })

            if current_ma <= 0:
                return jsonify({
                    "success": False,
                    "message": (
                        "Arus LED harus lebih dari 0 mA."
                    )
                })

            if supply <= led_voltage:
                return jsonify({
                    "success": False,
                    "message": (
                        "Tegangan sumber harus lebih besar "
                        "dari tegangan LED."
                    )
                })

            resistance = (
                supply - led_voltage
            ) / current_a

            return jsonify({
                "success": True,
                "result": (
                    "Rumus: R = (Vs - Vf) / I"
                    f"<br><strong>R = "
                    f"{format_resistance(resistance)}</strong>"
                )
            })


        # =================================================
        # 6. KODE WARNA RESISTOR
        # =================================================

        elif calculator == "color":

            bands = int(
                request.form.get("bands", 4)
            )

            color1 = request.form.get("color1")
            color2 = request.form.get("color2")
            color3 = request.form.get("color3")

            multiplier_color = request.form.get(
                "multiplier"
            )

            tolerance_color = request.form.get(
                "tolerance"
            )

            if bands == 4:

                digit = (
                    COLOR_VALUES[color1] * 10
                    + COLOR_VALUES[color2]
                )

            elif bands == 5:

                digit = (
                    COLOR_VALUES[color1] * 100
                    + COLOR_VALUES[color2] * 10
                    + COLOR_VALUES[color3]
                )

            else:

                return jsonify({
                    "success": False,
                    "message": (
                        "Jumlah gelang harus 4 atau 5."
                    )
                })

            resistance = (
                digit
                * COLOR_MULTIPLIER[multiplier_color]
            )

            tolerance = COLOR_TOLERANCE.get(
                tolerance_color,
                20
            )

            minimum = resistance * (
                1 - tolerance / 100
            )

            maximum = resistance * (
                1 + tolerance / 100
            )

            return jsonify({
                "success": True,
                "result": (
                    f"<strong>Nilai resistor = "
                    f"{format_resistance(resistance)}</strong>"
                    f"<br>Toleransi = ±{tolerance}%"
                    f"<br>Nilai minimum = "
                    f"{format_resistance(minimum)}"
                    f"<br>Nilai maksimum = "
                    f"{format_resistance(maximum)}"
                )
            })


        # =================================================
        # 7. ENERGI LISTRIK
        # =================================================

        elif calculator == "energy":

            power = float(
                request.form.get("power")
            )

            time = float(
                request.form.get("time")
            )

            if power < 0 or time < 0:
                return jsonify({
                    "success": False,
                    "message": "Nilai tidak boleh negatif."
                })

            energy = power * time

            return jsonify({
                "success": True,
                "result": (
                    "Rumus: E = P × t"
                    f"<br><strong>E = "
                    f"{energy:.4f} Wh</strong>"
                )
            })


        # =================================================
        # 8. PEMBAGI TEGANGAN
        # =================================================

        elif calculator == "divider":

            voltage = float(
                request.form.get("divider_voltage")
            )

            r1 = float(
                request.form.get("divider_r1")
            )

            r2 = float(
                request.form.get("divider_r2")
            )

            if voltage < 0:
                return jsonify({
                    "success": False,
                    "message": (
                        "Tegangan tidak boleh negatif."
                    )
                })

            if r1 <= 0 or r2 <= 0:
                return jsonify({
                    "success": False,
                    "message": (
                        "R1 dan R2 harus lebih dari 0 Ω."
                    )
                })

            output = voltage * (
                r2 / (r1 + r2)
            )

            return jsonify({
                "success": True,
                "result": (
                    "Rumus: Vout = Vin × R2 / (R1 + R2)"
                    f"<br><strong>Vout = "
                    f"{output:.4f} V</strong>"
                )
            })


        # =================================================
        # 9. KAPASITOR
        # =================================================

        elif calculator == "capacitor":

            mode = request.form.get(
                "capacitor_mode"
            )

            c1 = float(
                request.form.get("c1")
            )

            c2 = float(
                request.form.get("c2")
            )

            if c1 <= 0 or c2 <= 0:
                return jsonify({
                    "success": False,
                    "message": (
                        "Nilai kapasitor harus lebih dari 0."
                    )
                })

            if mode == "series":

                total = (
                    c1 * c2
                ) / (
                    c1 + c2
                )

                formula = (
                    "Ctotal = C1 × C2 / (C1 + C2)"
                )

            elif mode == "parallel":

                total = c1 + c2

                formula = "Ctotal = C1 + C2"

            else:

                return jsonify({
                    "success": False,
                    "message": (
                        "Pilih jenis rangkaian kapasitor."
                    )
                })

            return jsonify({
                "success": True,
                "result": (
                    f"Rumus: {formula}"
                    f"<br><strong>Ctotal = "
                    f"{format_capacitance(total)}</strong>"
                )
            })


        # =================================================
        # 10. KONVERSI SATUAN
        # =================================================

        elif calculator == "conversion":

            value = float(
                request.form.get(
                    "conversion_value"
                )
            )

            unit = request.form.get(
                "conversion_unit"
            )

            prefix_from = request.form.get(
                "prefix_from"
            )

            prefix_to = request.form.get(
                "prefix_to"
            )

            if value < 0:
                return jsonify({
                    "success": False,
                    "message": (
                        "Nilai tidak boleh negatif."
                    )
                })

            if unit not in UNIT_NAMES:
                return jsonify({
                    "success": False,
                    "message": (
                        "Jenis satuan tidak valid."
                    )
                })

            base_value = (
                value * PREFIX[prefix_from]
            )

            converted = (
                base_value / PREFIX[prefix_to]
            )

            symbol = UNIT_NAMES[unit]

            from_symbol = (
                PREFIX_SYMBOL[prefix_from]
                + symbol
            )

            to_symbol = (
                PREFIX_SYMBOL[prefix_to]
                + symbol
            )

            return jsonify({
                "success": True,
                "result": (
                    f"<strong>{value:g} "
                    f"{from_symbol} = "
                    f"{converted:g} "
                    f"{to_symbol}</strong>"
                )
            })


        return jsonify({
            "success": False,
            "message": "Kalkulator tidak ditemukan."
        })


    except ValueError:

        return jsonify({
            "success": False,
            "message": "Masukkan angka yang valid."
        })

    except KeyError:

        return jsonify({
            "success": False,
            "message": "Data yang dimasukkan tidak valid."
        })

    except ZeroDivisionError:

        return jsonify({
            "success": False,
            "message": (
                "Tidak dapat melakukan pembagian dengan nol."
            )
        })


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)