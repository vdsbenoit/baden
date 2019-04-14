import QrScanner from "/static/js/qr-scanner.min.js";
QrScanner.WORKER_PATH = '/static/js/qr-scanner-worker.min.js';

const previewDiv = $('#camera-preview-div');
const preview 	 = document.getElementById('camera-preview');
const noCameraErrorDiv 	 = $('#no-camera-error');
const closePreviewButton = $('#close-camera-preview');

var scanner = null;
var currentScanSource = null;

function startScan(source, callback)
{
	if (scanner != null)
	{
		scanner._onDecode = callback;
		currentScanSource.removeClass('activated-button');
		source.addClass('activated-button');
		currentScanSource = source;
	}
	else if (QrScanner.hasCamera())
	{
		scanner = new QrScanner(preview, result => callback(result));
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
function setPlayerResult(result)
{
    stopScan();
    $('#player-team-code').val(result);
}
function setGameResult(result)
{
    stopScan();
    $('#game-number').text(result).change();
}
function setGameName()
{
    $.ajax({
		url: 'api/get_game_name',
		type: 'GET',
		dataType: 'text',
		data: {
			'game_number': $('#game-number').val()
		}
	}).done(function (data) {
		$('#game-name').text(data);
		if (data.substring(0,5) == "Error")
		{
			$('#game-name').addClass('error-message');
		}
	}).fail(function () {
		alert("Could not contact server");
	});
}
function setTeamName(teamIndex)
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
			$('#team' + teamIndex + '-name').text(data);
			if (data.substring(0,5) == "Error")
			{
				$('#team' + teamIndex + '-name').addClass('error-message');
			}
			else
			{
				$('#team' + teamIndex + '-name').removeClass('error-message');
				$('#option-team' + teamIndex).val(data);
				$('#option-team' + teamIndex).text(teamCode + ' - ' + data);
			}
		}).fail(function () {
			alert("Could not contact server");
		});
	}
}
function setTeam1Result(result)
{
    stopScan();
	$('#team1-code').val(result).change();
}
function setTeam2Result(result)
{
    stopScan();
	$('#team2-code').val(result).change()
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
				if (data.substring(0,5) != "Error")
				{
					$('#team2-code').val(data).change();
				}
				else
				{
					alert(data);
				}
			}).fail(function () {
			alert("Could not contact server");
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
				if (data.substring(0,5) != "Error")
				{
					$('#team1-code').val(data).change();
				}
				else
				{
					alert(data);
				}
			}).fail(function () {
			alert("Could not contact server");
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
				if (data.substring(0,5) != "Error")
				{
					$('#game-number').val(data).change();
				}
				else
				{
					alert(data);
				}
			}).fail(function () {
			alert("Could not contact server");
		});
		}
	}
}

$(document).ready(function()
{
	closePreviewButton.click(stopScan);
	$('#player-qr-code-button').click(function() {startScan(('#player-qr-code-button'), setPlayerResult);});
	$('#scan-game-button').click(function() {startScan($('#scan-game-button'), setGameResult);});
	$('#scan-team1-button').click(function() {startScan($('#scan-team1-button'), setTeam1Result);});
	$('#scan-team2-button').click(function() {startScan($('#scan-team2-button'), setTeam2Result);});
	$('#team1-code').change(function() {setTeamName(1);});
	$('#team2-code').change(function() {setTeamName(2);});
	$('#game-number').change(setGameName);
	$('#team1-code').change(autoComplete);
	$('#team2-code').change(autoComplete);
	$('#game-number').change(autoComplete);
	$('#camera-preview').on('play', function(){previewDiv.slideDown(400);});
});