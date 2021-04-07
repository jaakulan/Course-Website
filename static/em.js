let ops = document.querySelectorAll('option');
ops[0].addEventListener('click',getmarks);
ops[1].addEventListener('click',getmarks);

async function getmarks(e) {
    let person = e.target.getAttribute('value');
    const url='http://localhost:5000/getmarks?user='+person
    const response = await fetch(url);
    const jsn = await response.json(); //extract JSON from the http response
    console.log(jsn);
    document.getElementById('user').setAttribute('value',person);

    let elems = document.querySelectorAll('input.score');
    //a1
    elems[0].setAttribute('placeholder',jsn['a1'])
    //a2
    elems[1].setAttribute('placeholder',jsn['a2'])
    //a3
    elems[2].setAttribute('placeholder',jsn['a3'])
    //midterm
    elems[3].setAttribute('placeholder',jsn['midterm'])
    //lab
    elems[4].setAttribute('placeholder',jsn['lab'])
    //final
    elems[5].setAttribute('placeholder',jsn['final'])
}

function getmarks2(e) {
    console.log("target: ", this.target);
    console.log("event: ", e.target);
}
