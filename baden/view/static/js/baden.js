import QrScanner from "/static/js/qr-scanner.min.js";
QrScanner.WORKER_PATH = '/static/js/qr-scanner-worker.min.js';

const NOTIFICATION_TIME = 8;
const previewDiv = $('#camera-preview-div');
const preview 	 = document.getElementById('camera-preview');
const noCameraErrorDiv 	 = $('#no-camera-error');
const closePreviewButton = $('#close-camera-preview');

var scanner = null;
var currentScanSource = null;

function startScan(source, targetFieldId)
{
	if (scanner != null)
	{
		scanner._onDecode = result => afterScan(result, targetFieldId);
		currentScanSource.removeClass('activated-button');
		source.addClass('activated-button');
		currentScanSource = source;
	}
	else if (QrScanner.hasCamera())
	{
		scanner = new QrScanner(preview, result => afterScan(result, targetFieldId));
		source.addClass('activated-button');
		currentScanSource = source;
		scanner.start();
	}
	else
	{
		noCameraErrorDiv.show();
	}
}
function stopScan()
{
	previewDiv.slideUp(200);
    scanner.destroy();
    scanner = null;
    currentScanSource.removeClass('activated-button');
    currentScanSource = null;

}
function afterScan(scanValue, targetFieldId){
	stopScan();
	$.ajax({
			url: 'api/resolve_hash',
			type: 'GET',
			dataType: 'text',
			data: {
				'value': scanValue
			}
		}).done(function(data){
			if (data.substring(0,5) == "Error")
			{
				alert(data.substring(7));
			}
			else
			{
				$('#' + targetFieldId).val(data).change();
			}
		})
		.fail(function () {
			alert("Error: could retrieve QR code data");
		});
}
function getGameName()
{
	let gameNumber = $('#game-number').val();
	if (gameNumber == "")
	{
		$('#game-name').text("");
	}
	else
	{
		$.ajax({
			url: 'api/get_game_name',
			type: 'GET',
			dataType: 'text',
			data: {
				'game_number': gameNumber
			}
		}).done(function (data) {
			if (data.substring(0,5) == "Error")
			{
				$('#game-name').addClass('error-message');
				$('#game-name').text(data.substring(7));
			}
			else
			{
				$('#game-name').removeClass('error-message');
				$('#game-name').text(data);
			}
		}).fail(function () {
			alert("Error: could retrieve game name");
		});
	}
}
function getTeamName(teamIndex)
{
	let teamCode = $('#team' + teamIndex + '-code').val();
	if (teamCode == "")
	{
		$('#team' + teamIndex + '-name').text("");
	}
	else
	{
		$.ajax({
			url: 'api/get_team_section',
			type: 'GET',
			dataType: 'text',
			data: {
				'team_code': teamCode
		 		}
		}).done(function (data) {
			if (data.substring(0,5) == "Error")
			{
				$('#team' + teamIndex + '-name').addClass('error-message');
				$('#team' + teamIndex + '-name').text(data.substring(7));
			}
			else
			{
				$('#team' + teamIndex + '-name').text(data);
				$('#team' + teamIndex + '-name').removeClass('error-message');
				$('#option-team' + teamIndex).val(teamCode);
				$('#option-team' + teamIndex).text(teamCode + ' - ' + data);
			}
		}).fail(function () {
			alert("Error: could retrieve team name");
		});
	}
}
function autoComplete(){
	let gameNumber = $('#game-number').val();
	let team1Code = $('#team1-code').val();
	let team2Code = $('#team2-code').val();
	if (gameNumber != "")
	{
		if (team1Code != "" && team2Code == "")
		{
			$.ajax({
				url: 'api/get_opponent_code',
				type: 'GET',
				dataType: 'text',
				data: {
					'team_code': team1Code,
					'game_number': gameNumber
			 		}
			}).done(function (data) {
				if (data.substring(0,5) == "Error")
				{
					alert(data.substring(7));
				}
				else if (data != "")
				{
					$('#team2-code').val(data).change();
				}
			}).fail(function () {
			alert("Error: could not autocomplete 1");
		});
		}
		if (team1Code == "" && team2Code != "")
		{
			$.ajax({
				url: 'api/get_opponent_code',
				type: 'GET',
				dataType: 'text',
				data: {
					'team_code': team2Code,
					'game_number': gameNumber
			 		}
			}).done(function (data) {
				if (data.substring(0,5) == "Error")
				{
					alert(data.substring(7));
				}
				else if (data != "")
				{
					$('#team1-code').val(data).change();
				}
			}).fail(function () {
			alert("Error: could not autocomplete 2");
		});
		}
	}
	else
	{
		if (team1Code != "" && team2Code != "")
		{
			$.ajax({
				url: 'api/get_game_number',
				type: 'GET',
				dataType: 'text',
				data: {
					'team1_code': team1Code,
					'team2_code': team2Code
			 		}
			}).done(function (data) {
				if (data.substring(0,5) == "Error")
				{
					alert(data.substring(7));
				}
				else if (data != "")
				{
					$('#game-number').val(data).change();
				}
			}).fail(function () {
			alert("Error: could not autocomplete 3");
		});
		}
	}
}

$(document).ready(function()
{
	if (document.getElementById('game-number') != null) getGameName();
	if (document.getElementById('team1-code') != null) getTeamName(1);
	if (document.getElementById('team2-code') != null) getTeamName(2);
	if (document.getElementById('team1-previous-code') != null) getTeamName('1-previous');
	if (document.getElementById('team2-previous-code') != null) getTeamName('2-previous');
	closePreviewButton.click(stopScan);
	$('#player-qr-code-button').click(function() {startScan($('#player-qr-code-button'), 'player-team-code');});
	$('#scan-game-button').click(function() {startScan($('#scan-game-button'), 'game-number');});
	$('#scan-team1-button').click(function() {startScan($('#scan-team1-button'), 'team1-code');});
	$('#scan-team2-button').click(function() {startScan($('#scan-team2-button'), 'team2-code');});
	$('#camera-preview').on('play', function(){previewDiv.slideDown(400);});
	$('#retry-button').click(function(){window.location = window.location.href.split("?")[0];});
	setTimeout(function(){
        $('.notification').slideDown(500);
        $('.warning').slideDown(500);
    }, 500);
	setTimeout(function(){
        $('.notification').slideUp(500);
        $('.warning').slideUp(500);
    }, (NOTIFICATION_TIME + 1) * 1000);
	$('#game-number').change(getGameName);
	$('#game-number').change(autoComplete);
	$('#player-team-code').change(function() {
		$('#player-team-code').val($('#player-team-code').val().toUpperCase());
		$('#get-score-button').click();
	});
	$('#team1-code').change(function() {
		$('#team1-code').val($('#team1-code').val().toUpperCase());
		getTeamName(1);
		autoComplete();
	});
	$('#team2-code').change(function() {
		$('#team2-code').val($('#team2-code').val().toUpperCase());
		getTeamName(2);
		autoComplete();
	});
});