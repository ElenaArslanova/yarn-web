
function BagOfElements() {
	
	this.getSynsetResults = function(parentElement) {
		var children = parentElement.getElementsByTagName('li');
		var correct = [];
		var wrong = [];
		for (var i=0; i < children.length; i++) {
			if (children[i].classList[1] === 'green-box')
				correct.push(children[i].textContent);
			else
				wrong.push(children[i].textContent);
		}
		correct = correct.join(';');
		wrong = wrong.join(';');
		return {'correct' : correct, 'wrong' : wrong, 'id' : parentElement.id};
	}
}

var bag = new BagOfElements();