from flask import Flask, render_template, request, redirect, session
app = Flask(__name__)
app.secret_key = "ALL 4 one, 1 for all."