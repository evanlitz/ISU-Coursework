package coms309.Cycino.follow;

import coms309.Cycino.users.User;
import coms309.Cycino.users.UserService;
import coms309.Cycino.users.UsersRepository;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class FollowService {
    @Autowired
    private FollowRepository followRepository;;
    @Autowired
    private UserService userService;
    @Autowired
    private UsersRepository repo;

    public List<Follow> getFollowingList(Long uid) {
        User user = userService.getUser(uid);
        return followRepository.findByUser(user);
    }

    @Transactional
    public boolean updateFollowing(Follow follow, Long uid) {
        boolean ok = false;
        User user = userService.getUser(uid);
        for (Follow item : user.getFollowList()){
            if (item.getFollowingID() == follow.getFollowingID()){
                item.setMuteNotifications(!(item.isMuteNotifications()));
                ok = true;
            }
        }
        return ok;
    }

    @Transactional
    public boolean blockUser(Follow follow, Long uid) {
        boolean ok = false;
        User user = userService.getUser(uid);
        for (Follow item : user.getFollowList()){
            if (item.getFollowingID() == follow.getFollowingID()){
                item.setBlockUser(true);
                ok = true;
                break;
            }
        }
        return ok;
    }

    @Transactional
    public boolean unblockUser(Follow follow, Long uid) {
        boolean ok = false;
        User user = userService.getUser(uid);
        for (Follow item : user.getFollowList()){
            if (item.getFollowingID() == follow.getFollowingID()){
                item.setBlockUser(false);
                ok = true;
                break;
            }
        }
        return ok;
    }

    @Transactional
    public boolean addToFollowList(Follow follow, Long uid) {
        boolean ok = true;
        User user = userService.getUser(uid);
        for (Follow item : user.getFollowList()){
            if (item.getFollowingID() == follow.getFollowingID()) {
                ok = false;
                break;
            }
        }
        if (ok) {user.newFollow(follow);}
        return ok;
    }

    @Transactional
    public boolean removeFromFollowList(Long uid, Long unfollowID) {
        User user = userService.getUser(uid);
        for (Follow item : user.getFollowList()){
            if (item.getFollowingID() == unfollowID) {
                user.removeFollow(item);
                followRepository.delete(item);
                repo.save(user);
                return true;
            }
        }
        return false;
    }

    public List<Long> getFollowers(Long uid) {
        List<Long> followersUIDs = new ArrayList<>();
        List<Follow> followers = followRepository.getFollowersByFollowingID(uid);
        for (Follow follow : followers) {
            followersUIDs.add(follow.getForeignKey());
        }
        return followersUIDs;
    }

}
