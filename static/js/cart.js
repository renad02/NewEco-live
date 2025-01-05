var updateBtns = document.getElementsByClassName('update-cart')   // updateBtns, Btns means buttons

for (i = 0; i < updateBtns.length; i++) {
	updateBtns[i].addEventListener('click', function(){         // function() is an action to do, function executes in each time we click
		var productId = this.dataset.product      // dataset.product, get it from html page wich is (product) in data-product={{product.id}} from stor page
		var action = this.dataset.action          // the seem thing put (action) in data-action="add"
		console.log('productId:', productId, 'Action:', action)

        console.log('USER:', user)             // get user from main.html in head -> var user = '{{request.user}}'
		if (user == 'AnonymousUser'){
			addCookieItem(productId, action)
			
		}else{
			//User is authenticated
            updateUserOrder(productId, action)
		}

	})
}


//Adding/Removing Items
function addCookieItem(productId, action){
	console.log('User is not authenticated')

	//cart will be like this, cart={1:{'quantity':4},}  | it means that number 1 is the product id and we pass the number of quantity that equal to 4 

	if (action == 'add'){     // If the action is "add", we want to check if this item is already in the cart.
		if (cart[productId] == undefined){
		cart[productId] = {'quantity':1}      // If not, then we create it

		}else{
			cart[productId]['quantity'] += 1    //If we already have that Item in our cart, we simply want to add to the quantity.
		}
	}

	if (action == 'remove'){      // If the action is "remove"
		cart[productId]['quantity'] -= 1  // we want to either decrease the quantity,

		if (cart[productId]['quantity'] <= 0){      //or, if the quantity is equal to or below zero, remove it from our cart altogether.
			console.log('Item should be deleted')
			delete cart[productId];
		}
	}
	console.log('CART:', cart)  
	document.cookie ='cart=' + JSON.stringify(cart) + ";domain=;path=/"    ////update the browsers cookie
	location.reload()
}


function updateUserOrder(productId, action){
	console.log('User is authenticated, sending data...')

		var url = '/update_item/'      // sending data to 

		fetch(url, {                   // we sent POST data so we use fetch, sending data to (url) and what kind of data we sent
			method:'POST',
			headers:{
				'Content-Type':'application/json',
				'X-CSRFToken':csrftoken,    // this is for handling error of sending data to backend  //this (csrftoken) from main.html
			}, 
			body:JSON.stringify({'productId':productId, 'action':action})   // body -> data we sent to database 
		})
		.then((response) => {         // the response after we sent data
		   return response.json();
		})
		.then((data) => {                 // data out in console
		    console.log('Data:', data)
			location.reload()
		});
}
