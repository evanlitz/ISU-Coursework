package coms309.Cycino.users;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class ChipService {

    @Autowired
    private UsersRepository repo;

    public Map<String, Object> add(long id, double chips){
        Map<String, Object> response = new HashMap<>();
        User u = repo.findById(id).orElse(null);
        if(u == null){
            response.put("status", 404);
            response.put("error", "no user with id");
            return response;
        }
        u.addChips(chips);
        repo.save(u);
        response.put("status", 200);
        response.put("chips", (int) u.getChips());
        return response;
    }

    public Map<String, Object> remove(long id, double chips){
        Map<String, Object> response = new HashMap<>();
        User u = repo.findById(id).orElse(null);
        if(u == null){
            response.put("status", 404);
            response.put("error", "no user with id");
            return response;
        }
        u.addChips(-1 * chips);
        repo.save(u);
        response.put("status", 200);
        response.put("chips", (int) u.getChips());
        return response;
    }

    public Map<String, Object> get(long id){
        Map<String, Object> response = new HashMap<>();
        User u = repo.findById(id).orElse(null);
        if(u == null){
            response.put("status", 404);
            response.put("error", "no user with id");
            return response;
        }
        response.put("status", 200);
        response.put("chips", (int) u.getChips());
        return response;
    }

}
