import QrScanner from "/static/js/qr-scanner.min.js";
QrScanner.WORKER_PATH = '/static/js/qr-scanner-worker.min.js';

const previewDiv = document.getElementById('camera-preview-div');
const preview = document.getElementById('camera-preview');
const noCameraErrorDiv = document.getElementById('no-camera-error');

const playerQrButton = document.getElementById('player-qr-code-button');
const playerCode = document.getElementById('player-team-code');

const team1QrButton = document.getElementById('team1-qr-code-button');
const team1Code = document.getElementById('team1-code');
const team2QrButton = document.getElementById('team2-qr-code-button');
const team2Code = document.getElementById('team2-code');
const gameQrButton = document.getElementById('game-qr-code-button');
const gameCode = document.getElementById('game-code');

var scanner = null;
var currentTarget = null;

function setResult(target, result)
{
    target.value = result;
    stopScan();
}

function startScan(target){
	previewDiv.style.display = 'block';
	if (QrScanner.hasCamera())
	{
		scanner = new QrScanner(preview, result => setResult(target, result));
		currentTarget = target;
		scanner.start();
	}
	else
	{
		noCameraErrorDiv.style.display = 'block';
	}
}

function stopScan(){
    scanner.destroy();
    currentTarget = null;
	previewDiv.style.display = 'none';

}

function toggleScan(target){
	if (currentTarget == target && target != null)
	{
		stopScan();
	}
	else
	{
		startScan(target);
	}

}

function setOnClickAction(button, target){
	if (button)
	{
		console.log("set action for " + target);
		button.onclick = function() {toggleScan(target)};
	}
}
setOnClickAction(playerQrButton, playerCode);
setOnClickAction(team1QrButton, team1Code);
setOnClickAction(team2QrButton, team2Code);
setOnClickAction(gameQrButton, gameCode);
