begining = """
<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="stylesheet" href="style.css" />
    <style>
    * {
margin: 0;
padding: 0;
box-sizing: border-box;
font-family: Arial, Helvetica, sans-serif;
font-size: 14px;
}


a {
	text-decoration: none;
	color: inherit;
	font-size: inherit;
}

.record a{
    margin-left: 10px;
}

a:hover {
	color: red; 
	text-decoration: none;
}

.container {	
	height: 100%;
	min-width: 960px;
	display: flex;
}

.left_side {
    position: fixed;
    display: flex;
    flex-direction: column;
    height: 100vh;
    gap: 4px;
    padding: 10px 0;
    justify-content: start;
	background-color: #eae8e8;
	width: 320px;
    min-width: 320px;
	margin: 0;
    overflow-y: auto;
    z-index: 2;
}

.info_button {
    margin: 0 10px;
    
    display: block;
    border: none;
    background-color: rgb(215, 187, 138);   
    padding: 14px;
    border-radius: 4px;
    text-align: center;
    cursor: pointer;
}
.info_button:hover {
    background-color: rgb(227, 197, 146);
    color: inherit;
   }

.line {
    display: block;
    width: 280px;
    margin: 10px auto;;
    border-bottom: 2px solid rgba(10, 10, 10, .2);
    

}    

.button {
    margin: 1px 10px;
    display: block;
    flex-shrink: 0;
    border: none;
    
    background-color: rgb(193, 186, 174);   
    padding: 14px;
    border-radius: 4px;
    text-align: center;
    cursor: pointer;
}

.button:hover {
    background-color: rgb(210, 202, 192);
}
      
.button:disabled {
    background-color: #c0c0c0;
    color:#7f7f7f;
    cursor: default;
    order: 200;
}

.active {
    background-color: rgb(227, 219, 208);
    outline:  2px solid  rgb(188, 181, 169); 
}
    
.right {
    position: flex;
    min-width: 960px;
    margin-left: 320px;
    /* left:320px; */
}

.record {
    display: flex;
    justify-content: start;
    column-gap: 3px;
	line-height: 1.5;
    padding-top: 4px;
    border-bottom: 1px solid #E8E8E8;
}


.record[hidden] {
    display: none;
}
/* .record:not([type="hidden"]):nth-child(odd) {background-color: #E8E8E8;} */

.record > span {
    display: block;
    
}
.number {
    position: relative;
    display: block;
    flex-shrink: 0;
    width: 56px;
    text-align: end;
}
.number .tooltip {
    position: absolute;
    display: inline-block;
    padding: 5px;
    width: max-content;
    max-width: 400px;
    text-align: start;
    font-size: 12px;
    background-color: #fff;
    border: 1px solid black;
    z-index: 10;
    visibility: hidden;
}

.number:hover .tooltip {
    visibility: visible;
}

.modal {
    position: fixed;
    display: flex;
    justify-content: center;
    align-items: center;
    top:0;
    left:0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, .8);
    visibility: hidden;
    opacity: 0;
    z-index: 10;
    cursor: pointer;
    overflow-y: auto;
}

.modal:target {
    visibility: visible;
    opacity: 1;
}

.modal__window {
    display:block;
    height: fit-content;
    max-width: 700px;
    min-width: 360px;
    background-color: #fff;
    overflow-y: auto;
    padding: 15px;
    margin: 15px;
    z-index: 15;
    cursor:auto;
    
}

.modal__window p {
font-size: 16px;
line-height: 1.3;
text-align: justify;
padding-top: 10px;
}

.modal a {
    display: block;
    position: fixed;
    text-align: center;
    width: 100%;
    height: 100%;
}

    </style>
    
</HEAD>
<body>	
<div class ="container">
	<div class = "left_side" id="left_side">
    <a href = "#popup" class="info_button">Об этом отчете</a>
    <span class="line"></span>
"""


inter = """
    </div> <!--  left side -->
	<div class = "right">
"""


ending = """
  </div>
  <div class="modal" id="popup">
    <a href="#left_side"></a>
    <div class="modal__window">
<p>Данный отчет позволяет просмотреть записанные файлы одним списком, вместо того чтобы скакать по каталогам и открывать файлы наугад.</p>

<p>Ключевая особенность данного отчета - возможность фильтровать список файлов, выбирая ключевые слова на левой панели. Фильтр применяется путем нажатия на кнопку с ключевым словом. При повторном нажатии кнопка отжимается. Одновременно можно нажать несколько кнопок. При этом в списке останутся только те файлы, в которых присутствуют все «нажатые» ключевые слова. Для сброса всех фильтров можно нажать кнопку "Все файлы".</p>

<p> На каждой кнопке указано количество файлов, содержащих данное ключевое слово. Если нажата одна кнопка, то цифры на других кнопках скорее всего уменьшатся. Они будут показывать, сколько файлов останется в списке поле нажатия следующей кнопки. После нажатия второй кнопки будут отображены файлы, содержащие оба ключевых слова. И так далее.</p>

<p>В ходе фильтрации некоторые кнопки могут отключиться и стать серыми. Это означает, что ни один из отображаемых файлов, не содержит указанного на кнопке ключевого слова. Нажимать такую кнопку бессмысленно, потому что при нажатии она бы отобразила в правой части экрана пустой список. То есть ничего.</p>

<p>Файлы в списке пронумерованы. При фильтрации по ключевым словам за каждым файлом сохраняется уникальный номер, так что впоследствии его будет легко найти. Кроме того, при наведении на номер файла, всплывает подсказка со списком ключевых слов, содержащихся в этом файле.</p>

<p>В отчете приводятся не оригинальные пути файлов, а обработанные, то есть, как они были записаны на данный носитель. Это связано с невозможностью повторить изначальный путь с точностью до буквы диска, а так же с тем, что часть файлов могут содержаться в архивах, и при копировании их пришлось разархивировать. Таким образом оригинальный путь <b>“D:\\temp\\архив.rar|Документ.xls”</b> в отчете будет представлен следующим образом: <b>“D\\temp\\архив.rar-ARCHIVE\\Документ.xls”</b>. Суффикс “-ARCHIVE” добавляется к имени архива специально для решения проблемы повторяющихся имен.</p>

<p>При нажатии на имя файла, он откроется в соседней вкладке браузера либо с помощью программы, связанной с данным типом файлов. Если браузер не знает, чем открыть данный файл, он предложит выбрать подходящую программу. Но файлы бывают разные, в том числе специфических форматов для специализированных программ, поэтому возможны случаи, когда некоторые файлы у вас не будут открываться, потому что на компьютере отсутствует нужное программное обеспечение.</p>

<p>И последнее: если ваш браузер давно не обновлялся (примерно с 2017 года и раньше), отчет может работать некорректно: например, не будут работать кнопки. Соответственно, нельзя будет отфильтровать список файлов.</p>  </div>
</div>
<script>
'use strict'

const btnColumn = document.querySelector('.left_side');
const buttons = [...btnColumn.querySelectorAll('.button')];
const records = Array.from(document.querySelectorAll('.record'));
const allButtonIds = buttons.map(btn => btn.id);
class Button {
    constructor(btn) {
        this.btn = btn;
        this.name = btn.dataset['keyword'];
        this.id = btn.id;
        this.qty = 0
    };

    get isPressed() {return this.btn.classList.contains('active')};
    
    press(event) {
        if (this.isPressed) {            
            this.turnOff();
        } else {
            this.turnOn();
        }
        return this.isPressed;
    }

    turnOn() {
        this.btn.classList.add('active');
    }

    turnOff() {
        this.btn.classList.remove('active');
    }

    disable() {
        if (this.qty>0) {
            this.btn.disabled = false;
        } else {
            this.btn.disabled = true;
        }

    }

    updateTextContent() {
        this.btn.textContent = `${this.name} (${this.qty})`
    }
}
class LeftButtons {
    constructor(objects) {
        this.buttons = objects
            .reduce((acc, button) => {acc[button.id] = new Button(button); return acc}, {});
        this.btnall = Object.values(this.buttons)
            .find(button => button.btn.dataset['keyword'] === "Все файлы");
        this.kw_counts = this.getKWCounts();
        this.updateTextContent();
        btnColumn.addEventListener('click', event =>  this.checkButtons(event) )
    }

    dropButtons() {
        Object.values(this.buttons).forEach(btn => btn.turnOff());
    }

    disableButtons() {
        Object.values(this.buttons).forEach(btn => btn.disable());
    }


    pressedButtonsKW() {
        return Object.values(this.buttons).reduce((acc, btn) => {
            if (btn.isPressed) {
                acc.push(btn.id)
            }
            return acc        
        }, []);    
    }

    checkButtons(event) {
        if (event.target.classList.contains('button')) {
            const t = event.target;            
            if (t == this.btnall.btn) {
                this.dropButtons();
                this.btnall.turnOn();
            } else {
                this.btnall.turnOff();
                this.buttons[t.id].press();
            }
            const pbkw = this.pressedButtonsKW();
            if (!pbkw.length) {this.btnall.turnOn();}
            hide_mismatched(pbkw);
            this.kw_counts = this.getKWCounts();
            this.updateTextContent();  
            this.disableButtons();
        }
    }
    getKWCounts() {
        let keywords_count = allButtonIds.reduce( (acc, k ) => {acc[k] = 0; return acc}, {});
        records.forEach(rec => {
            if (!rec.hidden) {
                rec.classList.forEach(cls => keywords_count[cls]++);
            }
        });
        keywords_count[this.btnall.id] = records.length
        return keywords_count;
    }
    
    updateTextContent() {
        for (let i in this.buttons) {
            this.buttons[i].qty = this.kw_counts[this.buttons[i].id]
            this.buttons[i].updateTextContent();
        }
    }
}
function hide_mismatched(keywords) {
    records.forEach(rec => {
        const rcl = [...rec.classList];
        if (keywords.every(kw => rcl.includes(kw))) {
            rec.hidden = false;
        } else {
            rec.hidden = true;
        }
    })
}
const cl = new LeftButtons(buttons)
</script>
</body>
</HTML>
"""
