class Media {
  constructor(title, isCheckedOut=false, ratings=[]) {
    this._title = title;
    this._isCheckedOut = isCheckedOut;
    this._ratings = ratings;
  }
  get title() {
    return this._title;
  }
  get isCheckedOut() {
    return this._isCheckedOut;
  }
  get ratings() {
    return this._ratings;
  }
  set isCheckedOut(toggle) {
    return this._isCheckedOut = toggle;
  }
  getAverageRating() {
    let avgRating = 0;
    this._ratings.forEach(rating => avgRating += rating);
    return avgRating / this._ratings.length; 
  }
  toggleCheckOutStatus() {
    this._isCheckedOut = 
     !this._isCheckedOut;
  }
  addRating(rate1, rate2, rate3) {
    this._ratings.push(rate1, rate2, rate3);
  }
}
class Book extends Media {
  constructor(author, title, pages, isCheckedOut, ratings) {
    super(title, isCheckedOut, ratings)
    this._author = author;
    this._pages = pages;    
  }
  get author() {
    return this._author;
  }
  get pages() {
    return this._pages;
  }
} 
class Movie extends Media {
  constructor(director, title, runTime, isCheckedOut, ratings) {
    super(title, isCheckedOut, ratings)
    this._director = director;
    this._runTime = runTime;    
  }
  get director() {
    return this._director;
  }
  get runTime() {
    return this._runTime;
  }
} 
class CD extends Media {
  constructor(artist, title, isCheckedOut, songs, ratings) {
    super(title, isCheckedOut, ratings)
    this._author = author;
    this._songs = songs;    
  }
  get artist() {
    return this._artist;
  }
  get songs() {
    return this._songs;
  }
} 
const historyOfEverything = new Book('Bill', 'A Short History of Nearly Everything', 544)
console.log(historyOfEverything)
historyOfEverything.toggleCheckOutStatus();
historyOfEverything.addRating(4, 5, 5)
console.log(historyOfEverything)
console.log(historyOfEverything.getAverageRating())
const speed = new Movie('Jan de Bont', 'Speed', 116);
speed.toggleCheckOutStatus()
console.log(speed.isCheckedOut)
speed.addRating(1, 1, 5)
speed.getAverageRating()
console.log(speed, speed.getAverageRating())

