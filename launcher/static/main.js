let palyer_now = null;
let palyer_modal = null;

let desc_palyer = [
    {
        "name": "ЛОХОГРІН",
        "desc": "У юності ви зачитувались шкільними фанфіками й пробували викликати духа Гоголя через TikTok. Ваш мозок давно витік, але чарівна сила залишилась.",
        "desc_1": '"Тпер ви ходите в костюмі крольчихи щоб скрити позор віків"',
        "ops_1": "+ деш (ривок на шифт)",
        "ops_2": '+ зброя "желізна зубочистка"',
        "ops_neg": "- 10% соціальної адекватності (можливість потіряти контроль біля гравця на 2 сикунди)",
        "file": "eblan"
    }
]

function clos(name) {
    $('#' + name).hide(); 
}

function openModal(name) {
    $('#' + name).show(); 
}

function sendData() {
    $.post("/submit", { code: null }, function(data) {
        palyer_now = data["skin"]
    });
}

function modal_rener(val) {
    openModal('modal');

    palyer_modal = desc_palyer[val]["file"];

    $("#name").html(desc_palyer[val]["name"]);
    $("#descripe").html(desc_palyer[val]["desc"]);
    $("#descripe_1").html(desc_palyer[val]["desc_1"]);
    $("#neg").html(desc_palyer[val]["ops_neg"]);
    $("#pos_1").html(desc_palyer[val]["ops_2"]);
    $("#pos").html(desc_palyer[val]["ops_1"]);
}

// whail

let currentFrame = 1;
const maxFrames = 4;
const imgElement = $('.player');

setInterval(function() {
    currentFrame = currentFrame % maxFrames + 1;
    imgElement.attr('src', `/static/assets/${palyer_now}/Idle_${currentFrame}.png`);
}, 100);


let currentFrame_1 = 1;
const imgElement_1 = $('.player_modal');

setInterval(function() {
    currentFrame_1 = currentFrame_1 % maxFrames + 1;
    imgElement_1.attr('src', `/static/assets/${palyer_modal}/Idle_${currentFrame_1}.png`);
}, 100);

