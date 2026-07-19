import { Component, ChangeDetectionStrategy } from '@angular/core';

@Component({
  selector: 'app-ai-assistant',
  templateUrl: './ai-assistant.component.html',
  styleUrls: ['./ai-assistant.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AiAssistantComponent {
  title = 'AI Assistant';
  message = 'This module will be integrated after the GenAI team completes the AI service.';
}
