let palyer_now = null;
let palyer_modal = null;
let val_unix = 0;

let desc_palyer = [
    {
        "name": "ЛОХОГРІН",
        "desc": "У юності ви зачитувались шкільними фанфіками й пробували викликати духа Гоголя через TikTok. Ваш мозок давно витік, але чарівна сила залишилась.",
        "desc_1": '"Тпер ви ходите в костюмі крольчихи щоб скрити позор віків"',
        "ops_1": "+ 5% до уворотів",
        "ops_2": '+ зброя "желізна зубочистка"',
        "ops_neg": "- 10% соціальної адекватності (можливість потіряти контроль біля гравця на 2 сикунди)",
        "file": "eblan"
    },
    {
        "name": "ШЛЮПОКРИТ",
        "desc": "Колись ви працювали в ЗАГСі, тепер ваша злість на розлучення стала вашим щитом.",
        "desc_1": '"Тпер ви баран"',
        "ops_1": "+ неможливо вбити рандомом",
        "ops_2": '+ зброя "желізна зубочистка"',
        "ops_neg": "- 10% швидкості (всі рухи обдумані, як шлюбний контракт)",
        "file": "holub"
    },
    {
        "name": "ТОЛСТОПУЗ",
        "desc": "Ви велика, противна туша. З дитинства вас годували бомжами, і ви стали жирним та непробивним.",
        "desc_1": '"Тпер ви є в книзі рекордів гінеса"',
        "ops_1": "+ 40% до макс хп і до сопротівленія",
        "ops_2": '+ зброя "желізна зубочистка"',
        "ops_neg": "- 40% швидкості (ви повзите)",
        "file": "suka"
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

function modal_rener() {
    openModal('modal');

    $(".palyer_info_clu").html(val_unix)
    palyer_modal = desc_palyer[val_unix]["file"];

    $("#name").html(desc_palyer[val_unix]["name"]);
    $("#descripe").html(desc_palyer[val_unix]["desc"]);
    $("#descripe_1").html(desc_palyer[val_unix]["desc_1"]);
    $("#neg").html(desc_palyer[val_unix]["ops_neg"]);
    $("#pos_1").html(desc_palyer[val_unix]["ops_2"]);
    $("#pos").html(desc_palyer[val_unix]["ops_1"]);
}

function nex_p() {
    if (val_unix === 2) {
        val_unix = 0;
    } else {
        val_unix += 1;
    }

    modal_rener();
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

