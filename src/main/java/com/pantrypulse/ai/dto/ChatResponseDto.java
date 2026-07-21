package com.pantrypulse.ai.dto;
import lombok.Data;

@Data
public class ChatResponseDto {

    private boolean success;
    private String timestamp;
    private ChatDataDto data;
    private String message;

}