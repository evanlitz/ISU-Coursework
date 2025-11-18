package com.coms309.helloworld.repository;

import com.coms309.helloworld.entity.Message;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.coms309.helloworld.entity.Login;

@Repository
public interface LoginRepository extends JpaRepository<Login, Long> {
}
