package coms309.Cycino.follow;

import coms309.Cycino.users.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface FollowRepository extends JpaRepository<Follow, Integer> {
    List<Follow> findByUser(User user);
    List<Follow> getFollowersByFollowingID(Long followingID);
}
