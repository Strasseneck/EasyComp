
// clock variables
const startingMinutes = 10;
let time = startingMinutes * 60;
const countdownEl = document.getElementById('countdown');

// clock functions
function updateCountdown() {
    const minutes = Math.floor(time / 60);
    let seconds = time % 60;
    if (seconds < 10) {
        seconds = '0' + seconds;
    }
    countdownEl.innerHTML = `${minutes}:${seconds}`;
    time --;
}


function startClock() {
    setInterval(updateCountdown, 1000);
}
