using System;
using System.Collections.Generic;

namespace c25v001_CORE_00000012.Process
{
    public class MyDomainModel
    {
        // --- Identity ---
        public string Id { get; set; }
        public string Source { get; set; }

        // --- Payload ---
        public string RawContent { get; set; }

        // --- Lifecycle ---
        public List<string> Observations { get; } = new List<string>();

        // --- Factory ---
        public static MyDomainModel Parse(string rawContent)
        {
            if (rawContent == null) throw new ArgumentNullException(nameof(rawContent));

            return new MyDomainModel
            {
                RawContent = rawContent
            };
        }

        // --- Validation ---
        public List<string> Validate()
        {
            var errors = new List<string>();
            if (string.IsNullOrWhiteSpace(RawContent))
                errors.Add("RawContent must not be empty.");
            return errors;
        }

        public override string ToString() => $"MyDomainModel(Id={Id}, Source={Source})";
    }
}
