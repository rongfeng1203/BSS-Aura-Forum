import 'Review.css';
const stars = document.querySelectorAll('#star');

let result = 0;

stars.forEach((item, index) => {
    item.addEventListener('click', () => {
        console.log('you have clicked on star: ', index + 1);
        result = index + 1;
        UpdateDiv();
    });
});

const UpdateDiv = () => {
    console.log('hii line 16');
    stars.forEach((item, index) => {
        if (index < result) item.classList.add('active');
        else item.classList.remove('active');
    });
    document.getElementById('result').innerText = `${result} out of 5`;
};