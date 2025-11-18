package com.example.lobbypage;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import androidx.appcompat.app.AppCompatActivity;

public class LobbyPageActivity extends AppCompatActivity {

    private Button buttonCreateLobby;
    private ScrollView scrollViewUsers;
    private LinearLayout linearLayoutUsers;
    private EditText editTextUser;
    private Button buttonAddUser;
    private Button buttonDeleteUser;
    private Button buttonDeleteLobby;
    private Button buttonUserLobby;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.lobby_page_activity);

        buttonCreateLobby = findViewById(R.id.button_create_lobby);
        scrollViewUsers = findViewById(R.id.scroll_view_users);
        linearLayoutUsers = findViewById(R.id.linear_layout_users);
        editTextUser = findViewById(R.id.edit_text_user);
        buttonAddUser = findViewById(R.id.button_add_user);
        buttonDeleteUser = findViewById(R.id.button_delete_user);
        buttonDeleteLobby = findViewById(R.id.button_delete_lobby);
        buttonUserLobby = findViewById(R.id.button_user_lobby);

        // Initially hide all elements except the create lobby button
        scrollViewUsers.setVisibility(View.GONE);
        editTextUser.setVisibility(View.GONE);
        buttonAddUser.setVisibility(View.GONE);
        buttonDeleteUser.setVisibility(View.GONE);
        buttonDeleteLobby.setVisibility(View.GONE);
        buttonUserLobby.setVisibility(View.GONE);

        // Set up click listener for create lobby button
        buttonCreateLobby.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                buttonCreateLobby.setVisibility(View.GONE);
                scrollViewUsers.setVisibility(View.VISIBLE);
                editTextUser.setVisibility(View.VISIBLE);
                buttonAddUser.setVisibility(View.VISIBLE);
                buttonDeleteUser.setVisibility(View.VISIBLE);
                buttonDeleteLobby.setVisibility(View.VISIBLE);
                buttonUserLobby.setVisibility(View.VISIBLE);
            }
        });

        // Set up click listener for delete lobby button
        buttonDeleteLobby.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                scrollViewUsers.setVisibility(View.GONE);
                editTextUser.setVisibility(View.GONE);
                buttonAddUser.setVisibility(View.GONE);
                buttonDeleteUser.setVisibility(View.GONE);
                buttonDeleteLobby.setVisibility(View.GONE);
                buttonUserLobby.setVisibility(View.GONE);
                buttonCreateLobby.setVisibility(View.VISIBLE);
            }
        });

        // Additional logic for buttonAddUser, buttonDeleteUser, buttonUserLobby can be added here
    }
}
