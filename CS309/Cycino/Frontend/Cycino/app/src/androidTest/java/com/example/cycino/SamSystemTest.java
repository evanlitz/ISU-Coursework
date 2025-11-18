package com.example.cycino;

import com.example.cycino.LoginActivity;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;

import androidx.core.widget.TextViewCompat;
import androidx.test.espresso.intent.Intents;
import androidx.test.ext.junit.rules.ActivityScenarioRule;
import androidx.test.filters.LargeTest;
import androidx.test.internal.runner.junit4.AndroidJUnit4ClassRunner;
import androidx.test.rule.ActivityTestRule;

import static androidx.test.espresso.Espresso.onView;
import static androidx.test.espresso.action.ViewActions.click;
import static androidx.test.espresso.action.ViewActions.closeSoftKeyboard;
import static androidx.test.espresso.action.ViewActions.typeText;
import static androidx.test.espresso.assertion.ViewAssertions.matches;
import static androidx.test.espresso.matcher.ViewMatchers.withId;
import static androidx.test.espresso.matcher.ViewMatchers.withText;
import static org.hamcrest.Matchers.not;



public class SamSystemTest {
    
    private final int WAIT_TIME = 2000;

    @Rule
    public ActivityScenarioRule<LoginActivity> activityScenarioRule = new ActivityScenarioRule<>(LoginActivity.class);

    @Test
    public void CreateDeleteAccount() {

        onView(withId(R.id.login_signup_btn)).perform(click());
        onView(withId(R.id.signup_username_edt)).perform(typeText("Testing2"), closeSoftKeyboard());
        onView(withId(R.id.signup_password_edt)).perform(typeText("Testing2"), closeSoftKeyboard());
        onView(withId(R.id.signup_confirm_edt)).perform(typeText("Testing2"), closeSoftKeyboard());

        onView(withId(R.id.signup_signup_btn)).perform(click());

        try {
            Thread.sleep(WAIT_TIME);
        } catch (InterruptedException e) {
        }

        onView(withId(R.id.settingsButton)).perform(click());
        onView(withId(R.id.accountSettingsButton)).perform(click());
        onView(withId(R.id.deleteAccountButton)).perform(click());

        try {
            Thread.sleep(WAIT_TIME);
        } catch (InterruptedException e) {}
        onView(withId(R.id.login_username_edt)).perform(typeText("Testing2"), closeSoftKeyboard());
        onView(withId(R.id.login_password_edt)).perform(typeText("Testing2"), closeSoftKeyboard());
        onView(withId(R.id.login_login_btn)).perform(click());

        onView(withId(R.id.login_username_edt)).check(matches(withText("Testing2")));


    }

    @Test
    public void Blackjack() {

        onView(withId(R.id.login_username_edt)).perform(typeText("Sam"), closeSoftKeyboard());
        onView(withId(R.id.login_password_edt)).perform(typeText("Craft"), closeSoftKeyboard());
        onView(withId(R.id.login_login_btn)).perform(click());

        try {
            Thread.sleep(WAIT_TIME);
        } catch (InterruptedException e) {}

        onView(withId(R.id.lobbyButton)).perform(click());

        try {
            Thread.sleep(WAIT_TIME);
        } catch (InterruptedException e) {}

        onView(withId(R.id.startButton)).perform(click());

        try {
            Thread.sleep(WAIT_TIME);
        } catch (InterruptedException e) {}

        onView(withId(R.id.dealButton)).perform(click());

        try {
            Thread.sleep(WAIT_TIME);
        } catch (InterruptedException e) {}

        onView(withId(R.id.backButton)).perform(click());

        try {
            Thread.sleep(WAIT_TIME);
        } catch (InterruptedException e) {}

        onView(withId(R.id.hpUsername)).check(matches(withText("Sam")));

    }

    @Test
    public void openLeaderboard() {

        onView(withId(R.id.login_username_edt)).perform(typeText("Sam"), closeSoftKeyboard());
        onView(withId(R.id.login_password_edt)).perform(typeText("Craft"), closeSoftKeyboard());
        onView(withId(R.id.login_login_btn)).perform(click());

        try {
            Thread.sleep(WAIT_TIME);
        } catch (InterruptedException e) {}

        onView(withId(R.id.leaderboardButton)).perform(click());
        onView(withId(R.id.blackjackLbButton)).perform(click());

        try {
            Thread.sleep(WAIT_TIME);
        } catch (InterruptedException e) {}

        onView(withId(R.id.lb_names)).check(matches(not(withText(""))));


    }

    @Test
    public void Login() {

        onView(withId(R.id.login_username_edt)).perform(typeText("Sam"), closeSoftKeyboard());
        onView(withId(R.id.login_password_edt)).perform(typeText("Craft"), closeSoftKeyboard());
        onView(withId(R.id.login_login_btn)).perform(click());

        try {
            Thread.sleep(WAIT_TIME);
        } catch (InterruptedException e) {}

        onView(withId(R.id.hpUsername)).check(matches(withText("Sam")));

    }





}


