// clock buttons
const btnStart = document.querySelector(".btn-start");
const btnPause = document.querySelector(".btn-pause");

// clock variables
const clock = document.getElementById('clock');
let clockInterval;
mins = 09;
secs = 60;
let paused = false;

// start clock function
startClock = () => {
    clockInterval = setInterval(function() {
    clock.style.color = 'green';

    // subtract second
    secs--;

    // clock display formatting
    let displayTime = '';
    if (mins < 10) {
        displayTime += '0' + mins;
    }
   
    else {
        displayTime += mins;
    }
    if (secs < 10) {
        displayTime += ':0' + secs;
    }

    else if (secs == 60) {
        displayTime += ':00';
    }
    else {
        displayTime += ':' + secs;
    }

    // check if seconds are 0
    if (secs == 0) {
        mins--;
        secs = 60;
    }

    // update clock innerhtml
    clock.innerHTML = displayTime;
   
    // capture value for pause
    pausedTime = displayTime;

    // pause clock function
    pauseClock = () => {
        paused = true;
        clearInterval(clockInterval)
        clock.innerHTML = pausedTime;
    }

    if (mins == 0 && secs < 10) {
        clock.style.color = 'red';
    }

    if (mins == -1) {
        clock.style.color = 'red';
        clearInterval(clockInterval);
        displayTime = '00:00';
    }

    }, 1000);
};

// buttons and score text competitor one
const scoreboard = document.querySelector('#scoreboard1')
const advantages = document.querySelector('#advantages1')
const penalties = document.querySelector('#penalties1')
const btns = document.querySelectorAll('.btn1')

// buttons and score text competitor two
const scoreboard2 = document.querySelector('#scoreboard2')
const advantages2 = document.querySelector('#advantages2')
const penalties2 = document.querySelector('#penalties2')
const btns2 = document.querySelectorAll('.btn2')

// initialize the score, advantages and penalties variables
let score1 = 0
let adv1 = 0
let pen1 = 0

let score2 = 0
let adv2 = 0
let pen2 = 0


btns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
        const styles = e.currentTarget.classList

        //adding scores
        if(styles.contains('+4pts')) {
            score1 += 4;
        }
        else if(styles.contains('+3pts')) {
            score1 += 3;
        }
        else if(styles.contains('+2pts')) {
            score1 += 2;
        }
        else if(styles.contains('+advantage')) {
            adv1 ++;
        }
        else if(styles.contains('+penalty')) {
            pen1 ++;
        }

        // subtracting scores 

        if(styles.contains('-4pts')) {
            score1 -= 4;
        }
        else if(styles.contains('-3pts')) {
            score1 -= 3;
        }
        else if(styles.contains('-2pts')) {
            score1 -= 2;
        }
        else if(styles.contains('-penalty')) {
            pen1 --;
        }

        if (score1 < 0) {
            score1 = 0;
        }

        if (adv1 < 0) {
            adv1 = 0;
        }

        if (pen1 < 0) {
            pen1 = 0;
        }

        if (score1 > 0) {
            scoreboard1.style.color = 'green';
        }

        if (score1 === 0) {
            scoreboard1.style.color = 'grey';
        }

        if (adv1 > 0) {
            advantages1.style.color = 'green';
        }

        if (adv1 === 0) {
            advantages1.style.color = 'grey';
        }

        if (pen1 > 0) {
            penalties1.style.color = 'red';
        }
        if (pen1 === 0) {
            penalties1.style.color = 'grey';
        }
        
        scoreboard.textContent = score1
        advantages.textContent = adv1
        penalties.textContent = pen1
    })
})


btns2.forEach((btn) => {
    btn.addEventListener('click', (e) => {
        const styles2 = e.currentTarget.classList

        //adding scores
        if(styles2.contains('+4pts')) {
            score2 += 4;
        }
        else if(styles2.contains('+3pts')) {
            score2 += 3;
        }
        else if(styles2.contains('+2pts')) {
            score2 += 2;
        }
        else if(styles2.contains('+advantage')) {
            adv2 ++;
        }
        else if(styles2.contains('+penalty')) {
            pen2 ++;
        }

        // subtracting scores 

        if(styles2.contains('-4pts')) {
            score2 -= 4;
        }
        else if(styles2.contains('-3pts')) {
            score2 -= 3;
        }
        else if(styles2.contains('-2pts')) {
            score2 -= 2;
        }
        else if(styles2.contains('-advantage')) {
            adv2 --;
        }
        else if(styles2.contains('-penalty')) {
            pen2 --;
        }

        if (score2 < 0) {
            score2 = 0;
        }

        if (adv2 < 0) {
            adv2 = 0;
        }

        if (pen2 < 0) {
            pen2 = 0;
        }

        if (score2 > 0) {
            scoreboard2.style.color = 'green';
        }

        if (score2 === 0) {
            scoreboard2.style.color = 'grey';
        }

        if (adv2 > 0) {
            advantages2.style.color = 'green';
        }

        if (adv2 === 0) {
            advantages2.style.color = 'grey';
        }

        if (pen2 > 0) {
            penalties2.style.color = 'red';
        }
        if (pen2 === 0) {
            penalties2.style.color = 'grey';
        }
        
        scoreboard2.textContent = score2
        advantages2.textContent = adv2
        penalties2.textContent = pen2
    })
})