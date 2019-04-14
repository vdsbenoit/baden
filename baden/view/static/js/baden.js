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
				$('#option-team' + teamIndex).val(data);
				$('#option-team' + teamIndex).text(teamCode + ' - ' + data);
			}
		}).fail(function () {
			alert("Error: could retrieve team name");
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
	closePreviewButton.click(stopScan);
	$('#player-qr-code-button').click(function() {startScan(('#player-qr-code-button'), setPlayerResult);});
	$('#scan-game-button').click(function() {startScan($('#scan-game-button'), setGameResult);});
	$('#scan-team1-button').click(function() {startScan($('#scan-team1-button'), setTeam1Result);});
	$('#scan-team2-button').click(function() {startScan($('#scan-team2-button'), setTeam2Result);});
	$('#team1-code').change(function() {getTeamName(1);});
	$('#team2-code').change(function() {getTeamName(2);});
	$('#game-number').change(getGameName);
	$('#team1-code').change(autoComplete);
	$('#team2-code').change(autoComplete);
	$('#game-number').change(autoComplete);
	$('#camera-preview').on('play', function(){previewDiv.slideDown(400);});
});