// Report switching; the hero video scrolls naturally with the page.
const reportButtons=[...document.querySelectorAll('[data-report-tab]')];
function showReport(index){reportButtons.forEach(button=>{const on=Number(button.dataset.reportTab)===index;button.classList.toggle('active',on);button.setAttribute('aria-pressed',String(on))});document.querySelectorAll('[data-report-card]').forEach(card=>card.hidden=Number(card.dataset.reportCard)!==index)}
reportButtons.forEach(button=>button.addEventListener('click',()=>showReport(Number(button.dataset.reportTab))));if(reportButtons.length)showReport(0);
