from flask import Flask, render_template, request
import pymysql
import binascii
import random
import os

app = Flask(__name__)

try:
    connection = pymysql.connect(
        host="localhost",
        port=3306,
        user="web",
        password="siteweb23854#&",
        database="shoreline",
    )
except Exception as ex:
    print("ошибка:", ex)


@app.route("/")
def index():
    with connection.cursor() as cursor:
        cursor.execute("SELECT lat, lon, date_i, id_i FROM images WHERE NOT EXISTS (SELECT 1 FROM banned WHERE "
                       "banned.id_i = images.id_i);")
        rows = cursor.fetchall()

        rndl = [random.randint(0, len(rows)-1)]
        rnd = rndl[0]
        while rnd == rndl[0]:
            rnd = random.randint(0, len(rows)-1)
        rndl.append(rnd)
        rnd = rndl[0]
        while rnd in rndl:
            rnd = random.randint(0, len(rows)-1)
        rndl.append(rnd)

        lst = [rows[rndl[0]][3], rows[rndl[1]][3], rows[rndl[2]][3]]

        lats = [rows[rndl[0]][0], rows[rndl[1]][0], rows[rndl[2]][0]]
        lons = [rows[rndl[0]][1], rows[rndl[1]][1], rows[rndl[2]][1]]
        dates = [str(rows[rndl[0]][2])[8:] + '-' + str(rows[rndl[0]][2])[5:7] + '-' + str(rows[rndl[0]][2])[:4],
                 str(rows[rndl[1]][2])[8:] + '-' + str(rows[rndl[1]][2])[5:7] + '-' + str(rows[rndl[1]][2])[:4],
                 str(rows[rndl[2]][2])[8:] + '-' + str(rows[rndl[2]][2])[5:7] + '-' + str(rows[rndl[2]][2])[:4]]

        lats2 = [rows[i][0] for i in range(len(rows))]
        lons2 = [rows[i][1] for i in range(len(rows))]

        if os.name == 'nt':
            sp = r'\ '[0]
        else:
            sp = '/'

        cursor.execute("SELECT picture FROM images WHERE images.id_i = " + str(lst[0]) + ";")
        rows = cursor.fetchall()
        with open(f'static{sp}img{sp}for_bd{sp}indexcard1.png', 'wb') as fle:
            fle.write(binascii.unhexlify(rows[0][0]))

        cursor.execute("SELECT picture FROM images WHERE images.id_i = " + str(lst[1]) + ";")
        rows = cursor.fetchall()
        with open(f'static{sp}img{sp}for_bd{sp}indexcard2.png', 'wb') as fle:
            fle.write(binascii.unhexlify(rows[0][0]))

        cursor.execute("SELECT picture FROM images WHERE images.id_i = " + str(lst[2]) + ";")
        rows = cursor.fetchall()
        with open(f'static{sp}img{sp}for_bd{sp}indexcard3.png', 'wb') as fle:
            fle.write(binascii.unhexlify(rows[0][0]))

    markers = [ {"coords": [lats2[i], lons2[i]], "text": f"{ lats2[i] } { lons2[i] }"} for i in range(len(lats2)) ]

    return render_template("index.html", lats=lats, lons=lons, dates=dates, markers=markers)


@app.route("/result",methods=["POST"])
def result():
    try:
        lati = float(request.form.get('ser').split(' ')[0])
        long = float(request.form.get('ser').split(' ')[1])
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT date_i, time_i, lon, lat, picture FROM images WHERE lon >= {long - 0.001} AND "
                           f"lon <= {long + 0.001} AND lat >= {lati - 0.001} AND lat <= {lati + 0.001} ORDER BY date_i;")
            rows = cursor.fetchall()

            if os.name == 'nt':
                sp = r'\ '[0]
            else:
                sp = '/'

            with open(f'static{sp}img{sp}for_bd{sp}rcard1.png', 'wb') as fle:
                fle.write(binascii.unhexlify(rows[0][4]))

            dates = [str(rows[0][0])[8:] + '-' + str(rows[0][0])[5:7] + '-' + str(rows[0][0])[:4]]
            try:
                times = [str(rows[0][1])]
            except:
                times = ['не указано']
            lons = [str(rows[0][2])]
            lats = [str(rows[0][3])]

            try:
                with open(f'static{sp}img{sp}for_bd{sp}rcard2.png', 'wb') as fle:
                    fle.write(binascii.unhexlify(rows[1][4]))
                dates.append(str(rows[1][0])[8:] + '-' + str(rows[1][0])[5:7] + '-' + str(rows[1][0])[:4])
                try:
                    times.append(str(rows[1][1]))
                except:
                    times.append('не указано')
                lons.append(str(rows[1][2]))
                lats.append(str(rows[1][3]))
            except:
                with open(f'static{sp}img{sp}for_bd{sp}zero.png', 'rb') as fle:
                    with open(f'static{sp}img{sp}for_bd{sp}rcard2.png', 'wb') as fle2:
                        fle2.write(fle.read())
                dates.append('')
                times.append('')
                lons.append('')
                lats.append('')

            try:
                with open(f'static{sp}img{sp}for_bd{sp}rcard3.png', 'wb') as fle:
                    fle.write(binascii.unhexlify(rows[2][4]))
                dates.append(str(rows[2][0])[8:] + '-' + str(rows[2][0])[5:7] + '-' + str(rows[2][0])[:4])
                try:
                    times.append(str(rows[2][1]))
                except:
                    times.append('не указано')
                lons.append(str(rows[2][2]))
                lats.append(str(rows[2][3]))
            except:
                with open(f'static{sp}img{sp}for_bd{sp}zero.png', 'rb') as fle:
                    with open(f'static{sp}img{sp}for_bd{sp}rcard3.png', 'wb') as fle2:
                        fle2.write(fle.read())
                dates.append('')
                times.append('')
                lons.append('')
                lats.append('')

        return render_template('result.html', dates=dates, times=times, lons=lons, lats=lats)
    except Exception as ex:
        print(ex)
        return render_template('sory.html')


@app.route('/update_coords', methods=['POST'])
def update_coords():
    data = request.json
    lat = data['lat']
    lng = data['lng']

    # Сохраните координаты в переменную Flask или выполните другую необходимую обработку

    return 'Coordinates received: lat={}, lng={}'.format(lat, lng)


if __name__ == "__main__":
    app.run(debug=True)