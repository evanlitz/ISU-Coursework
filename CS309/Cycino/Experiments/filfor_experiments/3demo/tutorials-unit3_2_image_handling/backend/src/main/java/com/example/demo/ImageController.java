package com.example.demo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.List;

@RestController
public class ImageController {

    // replace this! careful with the operating system in use
    // Trying relative path
    //private static String directory = System.getProperty("user.dir") + File.separator + "src" + File.separator + "main" + File.separator + "resources" + File.separator + "images";
    private static String directory = "C:" + File.separator + "Users" + File.separator + "filip" + File.separator + "test_folder";
    @Autowired
    private ImageRepository imageRepository;

    @GetMapping(value = "/images/{id}", produces = MediaType.IMAGE_JPEG_VALUE)
    byte[] getImageById(@PathVariable int id) throws IOException {
        System.out.println(directory);
        List<Image> images = imageRepository.findAll();
        System.out.println(images);
        Image image = imageRepository.findById(id);
        System.out.println(image);
        File imageFile = new File(image.getFilePath());
        return Files.readAllBytes(imageFile.toPath());
    }

    @GetMapping(value = "/images/local/apple", produces = MediaType.IMAGE_JPEG_VALUE)
    byte[] getAppleImage() throws IOException {
        ClassPathResource classPathResource = new ClassPathResource("/images/1.png");
        File imageFile = new File(classPathResource.getFile().getAbsolutePath());
        System.out.println(imageFile);
        System.out.println(imageFile.toPath());
        return Files.readAllBytes(imageFile.toPath());
    }

    @GetMapping(value = "/images/local/banana", produces = MediaType.IMAGE_JPEG_VALUE)
    byte[] getBananaImage() throws IOException {
        ClassPathResource classPathResource = new ClassPathResource("/images/2.jpg");
        File imageFile = new File(classPathResource.getFile().getAbsolutePath());
        System.out.println(imageFile);
        System.out.println(imageFile.toPath());
        return Files.readAllBytes(imageFile.toPath());
    }


    @PostMapping("/images")
    public String handleFileUpload(@RequestParam("image") MultipartFile imageFile)  {
        System.out.println("handleFileUpload");
        try {
            System.out.println(directory);
            File destinationFile = new File(directory + File.separator + imageFile.getOriginalFilename());
            System.out.println(destinationFile.getAbsolutePath());
            imageFile.transferTo(destinationFile);  // save file to disk
            //File newDestinationFile = new File(System.getProperty("java.io.tmpdir"));
            //imageFile.transferTo(newDestinationFile);
            System.out.println("imageFile.transferTo(x) -- Successful!");
            System.out.println(imageFile.getOriginalFilename());
            Image image = new Image();
            image.setFilePath(destinationFile.getAbsolutePath());
            imageRepository.save(image);
            System.out.println(imageRepository);
            return "File uploaded successfully: " + destinationFile.getAbsolutePath();
        } catch (IOException e) {
            return "Failed to upload file: " + e.getMessage();
        }
    }

}
