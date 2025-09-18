from flask import Flask,request,render_template
import pickle
from surprise import SVD,Reader,Dataset
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
movies=pd.read_csv(r"C:\Users\desai\OneDrive\Desktop\niti\Dataset\archive\movies.csv")
ratings=pd.read_csv(r"C:\Users\desai\OneDrive\Desktop\niti\Dataset\archive\ratings.csv")
tag=pd.read_csv(r"C:\Users\desai\OneDrive\Desktop\niti\Dataset\archive\tags.csv")
with open('svd_model.pkl','rb') as f:
    svd=pickle.load(f)
def recommend_svd(user_id,n=10):
    prediction=[]
    for movie in movies['movieId']:
        predict=svd.predict(user_id,movie).est
        prediction.append((movie,predict))
    top_n=sorted(prediction,key=lambda x: x[1],reverse=True)[:n]
    print(f"Top {n} recommendation for User {user_id}:")
    titles=[]
    for movie,score in top_n:
        title=movies[movies['movieId']==movie]['title'].values[0]
        titles.append(title)
        #print("-",title,f"(pred {score:.2f})")
    return titles
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recommendations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
class User_recommendation_table(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,nullable=False)
    movie_titles=db.Column(db.Text,nullable=False)
@app.route('/',methods=['GET','POST'])
def home():
    recommendations=None
    user_id=None
    if request.method=='POST':
        user_id=int(request.form['user_id'])
        recommendations=recommend_svd(user_id,n=10)
        rec_db=",".join(recommendations)
        existing=User_recommendation_table.query.filter_by(user_id=user_id).first()
        if existing:
            existing.movie_titles=rec_db
        else:
            new_db=User_recommendation_table(user_id=user_id,movie_titles=rec_db)
            db.session.add(new_db)
        db.session.commit()
    return render_template('home.html',recommendations=recommendations,user_id=user_id)
if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)