var scanner = new Instascan.Scanner({
    video: document.getElementById('preview'),
    continuous: true,
    mirror: false,
    captureImage: false,
    backgroundScan: false,
    scanPeriod: 5
});
scanner.addListener('scan', function (content) {
    console.log("QR code found: " + content);
    $('#player-team-code').value(content);
    scanner.stop();
});
function startScan() {
Instascan.Camera.getCameras().then(function (cameras) {
    if (cameras.length > 0) {
        scanner.start(cameras[0]);
    } else {
        console.error('No cameras found.');
    }
}).catch(function (e) {
    console.error(e);
});
}
$(document).ready(function() {
    $('#player-qr-code-button').click(startScan);
});