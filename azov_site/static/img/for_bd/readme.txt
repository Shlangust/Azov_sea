index.html

в <div class=card>

ты редачишь scr="{{ url_for('static', filename=ТУТ ВСТАВЛЯЕШЬ ПУТЬ  ФАЙЛА СТРОКОЙ) }}"

в result

в images 

<div class="image_1">
            <img class="image_1", src="{{ url_for('static', filename=ТУТ ВСТАВЛЯЕШЬ ПУТЬ  ФАЙЛА СТРОКОЙ) }}">


тут может быть проблема с f строками поэтому если что попробуй 
s +='{{ url_for('static', filename='
s += ПУТЬ ДО КАРТИКИ СТРОКОЙ
s += '}}'