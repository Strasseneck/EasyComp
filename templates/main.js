// buttons and score text
const scoreboard = document.querySelector('#scoreboard')
const advantages = document.querySelector('#advantages')
const penalties = document.querySelector('#penalties')
const btns = document.querySelectorAll('.btn')

// initialize the score, advantages and penalties variables
let score = 0
let adv = 0
let pen = 0


btns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
        const styles = e.currentTarget.classList

        //adding scores
        if(styles.contains('+4pts')) {
            score += 4;
        }
        else if(styles.contains('+3pts')) {
            score += 3;
        }
        else if(styles.contains('+2pts')) {
            score += 2;
        }
        else if(styles.contains('+advantage')) {
            adv ++;
        }
        else if(styles.contains('+penalty')) {
            pen ++;
        }

        // subtracting scores 

        if(styles.contains('-4pts')) {
            score -= 4;
        }
        else if(styles.contains('-3pts')) {
            score -= 3;
        }
        else if(styles.contains('-2pts')) {
            score -= 2;
        }
        else if(styles.contains('-advantage')) {
            adv --;
        }
        else if(styles.contains('-penalty')) {
            pen --;
        }

        if (score < 0) {
            score = 0;
        }

        if (adv < 0) {
            adv = 0;
        }

        if (pen < 0) {
            pen = 0;
        }

        if (score > 0) {
            scoreboard.style.color = 'green';
        }

        if (score === 0) {
            scoreboard.style.color = 'grey';
        }

        if (adv > 0) {
            advantages.style.color = 'green';
        }

        if (adv === 0) {
            advantages.style.color = 'grey';
        }

        if (pen > 0) {
            penalties.style.color = 'red';
        }
        if (pen === 0) {
            penalties.style.color = 'grey';
        }
        
        scoreboard.textContent = score
        advantages.textContent = adv
        penalties.textContent = pen
    })
})