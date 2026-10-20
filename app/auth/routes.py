from urllib.parse import urlparse
from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import Administrator
from app.auth.forms import LoginForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def is_safe_url(target):
    """Ensure redirect URL is strictly local to avoid open redirect vulnerabilities."""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Administrator login handler."""
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        admin = Administrator.query.filter_by(email=email).first()

        if admin:
            # Check for excessive failed attempts
            if admin.failed_login_attempts >= 10:
                flash(
                    "This account has been temporarily locked due to excessive failed attempts. Please contact systems support.",
                    "danger",
                )
                return render_template("auth/login.html", form=form)

            if admin.check_password(form.password.data):
                admin.failed_login_attempts = 0
                admin.last_login_at = datetime.now(timezone.utc)
                db.session.commit()

                login_user(admin, remember=form.remember_me.data)
                flash(f"Welcome back, {admin.name}!", "success")

                next_page = request.args.get("next")
                if next_page and is_safe_url(next_page):
                    return redirect(next_page)
                return redirect(url_for("admin.dashboard"))
            else:
                admin.failed_login_attempts += 1
                db.session.commit()

        # Generic failure message for security
        flash("Invalid email or password. Please verify your credentials.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """Sign out the current administrator."""
    logout_user()
    flash("You have been signed out safely.", "info")
    return redirect(url_for("auth.login"))
