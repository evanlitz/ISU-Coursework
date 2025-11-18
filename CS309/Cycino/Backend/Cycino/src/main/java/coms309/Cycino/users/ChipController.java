package coms309.Cycino.users;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
public class ChipController {

    @Autowired
    private ChipService service;

    @PutMapping("/chips/add/{id}/{chips}")
    public Map<String, Object> addChips(@PathVariable long id, @PathVariable double chips){
        return service.add(id, chips);
    }

    @PutMapping("/chips/remove/{id}/{chips}")
    public Map<String, Object> remove(@PathVariable long id, @PathVariable double chips){
        return service.remove(id, chips);
    }

    @GetMapping("/chips/get/{id}")
    public Map<String, Object> getChips(@PathVariable long id){
        return service.get(id);
    }

}
